$(".login-button").click(function() {
    $("#form-login").css("display", "inline-block");
    $(".form-background").css("display", "inline-block");

    $(".form-background,.form-close").click(function() {
        $("#form-login").css("display", "none");
        $(".form-background").css("display", "none");
    });
});

$(".sign-up-button").click(function() {
    $("#form-sign-up").css("display", "inline-block");
    $(".form-background").css("display", "inline-block");

    $(".form-background,.form-close").click(function() {
        $("#form-sign-up").css("display", "none");
        $(".form-background").css("display", "none");
    });
});



// $("#down-arrow").click(function() {
//     $('html, body').animate({
//         scrollTop: $("#learn-more").offset().top
//     }, 1000);
// });

// $(".sign-up-button").click(function() {
//     $("form").css("display", "inline-block");
// });


function login() {
}
// add an if condition: if user isn't logged in then set display: none to nav-bar
