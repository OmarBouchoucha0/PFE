const sidemenu = document.querySelector("aside");
const menubtn = document.querySelector("#menubtn");
const closebtn = document.querySelector("#closebtn");


//show sidebar
menubtn.addEventListener("click", ()=>{
    sidemenu.style.display ="block";
})

//hide sidebar
closebtn.addEventListener("click", ()=>{
    sidemenu.style.display ="none";
})
