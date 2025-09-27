$(document).ready(function() {
    const loginForm = $("form[action$='login']");
    if (loginForm.length) {
        loginForm.on('submit', function(e) {
            let valid = true;
            const username = $('#username').val().trim();
            const password = $('#password').val();
            if (!/^\w{3,}$/.test(username)) {
                $('#username').addClass('is-invalid');
                valid = false;
            } else {
                $('#username').removeClass('is-invalid');
            }
            
            if (!/^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d!@#$%^&*()_+\-=]{6,}$/.test(password)) {
                $('#password').addClass('is-invalid');
                valid = false;
            } else {
                $('#password').removeClass('is-invalid');
            }
            if (!valid) {
                e.preventDefault();
            }
        });
        $('#username, #password').on('input', function() {
            $(this).removeClass('is-invalid');
        });
    }
});
