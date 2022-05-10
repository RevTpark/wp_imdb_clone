


function validateSignIn(){
    let email = document.getElementById("email").value;
    let password = document.getElementById("password").value;

    let email_error = document.getElementById("email-error");
    let password_error = document.getElementById("password-error");
    email_error.innerHTML = "";
    password_error.innerHTML = "";

    if(email == "" || password == ""){
        if(email == ""){
            email_error.innerHTML = "Email cannot be blank.";
        }

        if(password == ""){
            password_error.innerHTML = "Password cannot be blank.";
        }
    }
    else{
        if(!email.includes("@") || !email.includes(".com")){
            email_error.innerHTML = "Enter a valid Email.";
        }
    }
}

function validateSignUp(){
    let name = document.getElementById("name").value;
    let email = document.getElementById("email").value;
    let address = document.getElementById("address").value;
    let city = document.getElementById("city").value;
    let number = document.getElementById("number").value;
    let pin_code = document.getElementById("pin-code").value;
    let password1 = document.getElementById("password1").value;
    let password2 = document.getElementById("password2").value;

    let name_error = document.getElementById("name-error");
    let email_error = document.getElementById("email-error");
    let address_error = document.getElementById("address-error");
    let city_error = document.getElementById("city-error");
    let number_error = document.getElementById("number-error");
    let pin_code_error = document.getElementById("pin-code-error");
    let password1_error = document.getElementById("password1-error");
    let password2_error = document.getElementById("password2-error");

    name_error.innerHTML = "";
    email_error.innerHTML = "";
    address_error.innerHTML = "";
    city_error.innerHTML = "";
    number_error.innerHTML = "";
    pin_code_error.innerHTML = "";
    password1_error.innerHTML = "";
    password2_error.innerHTML = "";

    if(name == "" || email == "" || address == "" || city == "" || number == "" || password1 == "" || password2 == "" || pin_code == ""){
        if(name == ""){ name_error.innerHTML = "Name cannot be blank"};
        if(email == ""){ email_error.innerHTML = "Email cannot be blank"};
        if(address == ""){ address_error.innerHTML = "Address cannot be blank"};
        if(city == ""){ city_error.innerHTML = "City cannot be blank"};
        if(number == ""){ number_error.innerHTML = "Number cannot be blank"};
        if(pin_code == ""){ pin_code_error.innerHTML = "Pin Code cannot be blank."};
        if(password1 == ""){ password1_error.innerHTML = "Password cannot be blank"};
        if(password2 == ""){ password2_error.innerHTML = "Password cannot be blank"};
    }
    else{
        if(!email.includes("@") || email.includes(".com")){
            email_error.innerHTML = "Enter a valid Email.";
        }
    
        if(number.length < 10 || number.length > 10){
            number_error.innerHTML = "Phone number should be of 10 digits only.";
        }
    
        if(pin_code.length > 6 || pin_code.length < 6){
            pin_code_error.innerHTML = "Pin Code should be of 6 digits only."
        }
    
        if(password1 != password2){
            password2_error.innerHTML = "Password did not match.";
        }
    }
} 

// $(document).ready(function() {
//     $("#owl-demo-v").owlCarousel({
//         autoPlay: 10000, //Set AutoPlay to 3 seconds
//         items : 1,
//         video : true,
//         itemsDesktop : [1199,3],
//         itemsDesktopSmall : [979,3]
//     });
// });
