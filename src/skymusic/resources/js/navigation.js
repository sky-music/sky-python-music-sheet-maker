function showLogo(elementId) {

    url = window.location.href;
    const regex = /{SKY_MUSIC_URL}/g;
    const found = url.match(regex);
    if (found) {
        navTable = document.getElementById(elementId);
        navTable.style.display = "inline";	
    }    
}
