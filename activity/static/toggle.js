function myFunction() {
    var element = document.querySelector('body');
    element.classList.toggle("dark-mode");
    
    if (document.querySelector('#bu1').innerHTML==="Dark mode"){
        document.querySelector('#bu1').innerHTML="Light mode";
        document.querySelector('#bu1').className="btn btn-outline-light";
        }
        
    else{
        document.querySelector('#bu1').innerHTML="Dark mode";
        document.querySelector('#bu1').className="btn btn-outline-dark";
        }

    if (document.querySelector('#nav1').className==="navbar navbar-expand-md navbar-light bg-light border")
    {
        document.querySelector('#nav1').className="navbar navbar-expand-md navbar-dark bg-dark border"
    }     
    else
    {
        document.querySelector('#nav1').className="navbar navbar-expand-md navbar-light bg-light border"
    }

    }