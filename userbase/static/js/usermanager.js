
$(document).ready(function() {
    jQuery.validator.addMethod("pw", function( value, element ) {
        return this.optional(element) || value.length >= 6 && /\d/.test(value) && /[a-z]/i.test(value);
    }, "Ihr Passwort muss mindestens 6 Zeichen lang sein und mindestens 1 Zahl und 1 Buchstaben enthalten.");

    $("form.validate").validate({
        onkeyup: false,
        highlight: function (element, errorClass, validClas) { 
            $(element).parents(".clearfix").addClass("error"); 
        }, 
        unhighlight: function (element, errorClass, validClass) { 
            $(element).parents(".error").removeClass("error"); 
        }, 
        errorElement: 'span',
        errorClass: "help-inline"
    }); 
});

