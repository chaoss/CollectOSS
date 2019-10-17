function saveConfigValues(event) {
    var data = { };
    $.each($('form').serializeArray(), function() {
        data[this.name] = this.value;
    });

    $.ajax({
        type: "POST",
        url: 'test/',
        data: data,
        contentType: 'application/x-www-form-urlencoded'
    })
}