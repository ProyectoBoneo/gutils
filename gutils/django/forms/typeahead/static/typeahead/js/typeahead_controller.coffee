class @TypeaheadController
    constructor: ->
        @cancel_add_button = $("#add_model_modal-cancel-button")
        @confirm_add_button = $("#add_model_modal-confirm-button")
        @modal_dialog = $("#add_model_modal")
        @contenedor = $("#contenedor_add_model")
        @sources = {}

    refresh_description: (form_input, typeahead_url, lookup_name, typeahead_input) ->
        url = typeahead_url + '?lookup=' + lookup_name + '&form_input_value=' + $(form_input).val()
        $.get(url, (data) -> $(typeahead_input).val(data.description))

    open_add_model_form: (typeahead_input) ->
        add_url = typeahead_input.getAttribute("data-add-url")
        $.get(add_url, (data) =>
            $(@contenedor).html(data)
            $(@modal_dialog).find("#modal_title").html(typeahead_input.getAttribute("data-lookup-model-description"))
            mainController.configure_controls()
            $(@modal_dialog).modal('show')
            $(@confirm_add_button).off('click')
            $(@confirm_add_button).click(=>@confirm_add_model_form(typeahead_input))
            $(@cancel_add_button).off('click')
            $(@cancel_add_button).click(=>@close_add_model_form()))
        

    confirm_add_model_form: (typeahead_input) ->
        add_url = typeahead_input.getAttribute("data-add-url")
        post_data = $(@contenedor).find("*").serialize()
        $.post(add_url,
               post_data,
               (data) =>
                    if(typeof data=="object")  # valido
                        $(typeahead_input).val(data.instance_id)
                        @close_add_model_form()
                    else  # invalido
                        $(@contenedor).html(data)
                        mainController.configure_controls()
        )

    close_add_model_form: -> $("#add_model_modal").modal('hide')

    get_source: (typeahead_url, lookup_name) ->
        if(lookup_name of @sources)
            return @sources[lookup_name]
        else
            source = new Bloodhound({
            hint: false,
            datumTokenizer: Bloodhound.tokenizers.obj.whitespace('description'),
            queryTokenizer: Bloodhound.tokenizers.whitespace,
            remote: typeahead_url + '?lookup=' + lookup_name + '&query=%QUERY'
            })
            source.initialize()
            @sources[lookup_name] = source
        return source

    register_typeaheads: ->
        typeahead_form_inputs = $(".typeahead-form-input").filter(->this.getAttribute("data-lookup-activated") == 'false')
        $(typeahead_form_inputs).each(
            (index, form_input)=>
                lookup_input_id = form_input.getAttribute("id") + "-typeahead"
                lookup_name = form_input.getAttribute("data-lookup-name")
                typeahead_url = form_input.getAttribute("data-lookup-url")
                initial_description = form_input.getAttribute("data-initial-description")

                form_group_div = form_input.parentNode.parentNode
                typeahead_div = form_input.parentNode

                typeahead_input_title = $(form_input).prop("title")

                typeahead_input = document.createElement('input')
                typeahead_input.setAttribute('type', 'text')
                if $(form_input).hasClass("with_errors")
                    typeahead_input.setAttribute('class', 'with_errors')
                typeahead_input.setAttribute('class', typeahead_input.getAttribute('class') + ' form-control')
                typeahead_input.setAttribute('title', typeahead_input_title)
                typeahead_input.setAttribute('id', lookup_input_id)
                typeahead_div.insertBefore(typeahead_input, form_input.nextSibling)

                label = $(form_group_div).find('label')
                if $(label).length == 1
                    $(label)[0].setAttribute('for', lookup_input_id)

                $(typeahead_input).typeahead(null,
                    {
                        name: lookup_name,
                        displayKey: 'description',
                        source: @get_source(typeahead_url, lookup_name).ttAdapter(),
                        minLength: 0
                    }
                    ).on('typeahead:selected', (object, datum) -> $(form_input).val(datum.id))

                $(typeahead_input).change(
                    ->
                        if $(this).val() == ''
                            $(form_input).val('')
                )

                $(form_input).watch('value',
                    =>
                        initial_value = form_input.getAttribute("data-initial-value")
                        initial_description = form_input.getAttribute("data-initial-description")
                        if $(form_input).val() != initial_value or $(typeahead_input).val() != initial_description
                            $(form_input).trigger('change')
                            @refresh_description(form_input, typeahead_url, lookup_name, typeahead_input)
                )

                typeahead = $(typeahead_input).data('ttTypeahead')
                dropdown = $(form_group_div).find("#" + lookup_input_id + "-dropdown")
                $(dropdown).off("click")
                $(dropdown).click(->
                    $(this).focus()
                    if not $(this).hasClass("data-clicked")
                        $(this).addClass("data-clicked")
                        typeahead._openResults()
                    else
                        $(this).removeClass("data-clicked")
                        typeahead._onBlurred()
                )
                $(dropdown).off("blur")
                $(dropdown).blur(
                    ->
                        typeahead._onBlurred()
                        $(dropdown).removeClass("data-clicked")
                )
                addmodel = $(form_group_div).find("#" + lookup_input_id + "-dropdown-add")
                $(addmodel).off('click')
                $(addmodel).click(
                    =>
                        @open_add_model_form(form_input)
                    )
                typeahead.input.setQuery(initial_description)
                $(typeahead_input).val(initial_description)
                form_input.setAttribute("data-lookup-activated", "true")
        )

window.typeaheadController = new TypeaheadController()
