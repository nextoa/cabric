(function () {


    $("#form").submit(function () {

//        $.ajax({
//
//            url: $(location).attr('href'),
//            method: 'post',
//            data: $('#form').serialize(),
//            success: function (data) {
//                $("#msg").append("<p>" + data + "</p>")
//            },
//            async: false
//        })

        ct = $("#msg iframe")
        ct.attr('src', "/process/?" + $(this).serialize())
        ct.removeClass("hide")
        return false
    })


    $("#refresh-tags").click(function () {

        $.getJSON("/tags/" + $(this).attr('project'), function (data) {
            $("#tags").empty()
            $("#tags").append("<option value='0'>默认</option>")
            for (tag in data.tags) {
                $("#tags").append("<option value='" + data.tags[tag] + "'>" + data.tags[tag] + "</option>")
            }
        })

    })

    $(document).ready(function(){
        $("#refresh-tags").trigger("click")
    })

})();