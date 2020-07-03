function showLogo(elementId) {

    url = window.location.href;
    const regex = /sky\-music\.github\.io/g;
    const found = url.match(regex);
    if (found) {
        navTable = document.getElementById(elementId);
        navTable.style.display = "inline";	
    }    
}
window.addEventListener("load", function(){showLogo('navigation')}, false);
