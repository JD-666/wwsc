$(function() {
    /* Ties the keyup even to this function which uses Ajax to send data to a 
    view. This data is send via a POST method and returns a template of html.
    We insert all the html returned into the #search-results element. */
    $('#search').keyup(function() {
        $.ajax({
            type: "POST",
            url: '/forum/search/',
            data: {
                'search_text' : $('#search').val(),
                'csrfmiddlewaretoken' : $("input[name=csrfmiddlewaretoken]").val(),
                'search_type' : $("input[name=SearchType]").val(),
                'search_category' : $("input[name=SearchCategory]").val()
            },
            success: searchSuccess,
            dataType: 'html'
        });
    });
});


function searchSuccess(data, textStatus, jqXHR) {
    $('#search-results').html(data);
}

function AuthenticateUser() {
    $('#login-result-div').html('<div class="text-info"><p>Attempting to login...</p></div>');
    setTimeout(auth_process,800);
}
function auth_process() {
    /* Uses Ajax to send POST information to be processed by a view. The view
    sends back a json object with a string in jason.result */
    $.ajax({
        type: "POST",
        url: "/forum/ajax_login/",
        datatype: "json",
        async: true,
        data: {
            csrfmiddlewaretoken: $("input[name=csrfmiddlewaretoken]").val(),
            username: $("#username").val(),
            password: $('#pwd').val(),
            remember: $('#remember').prop('checked')
        },
        success: function (json) {
            $('#login-result-div').html(json.result);
        }
    });
    //$('#login-result-div').html('<div id="login-result" class="alert alert-info"><p>Attempting to login...</p></div>');
}
