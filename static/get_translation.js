function setupTranslations() {
    var words = document.getElementsByClassName('word');
    for (var i = 0; i < words.length; i++) {
        words[i].addEventListener('click', function (event) {
            var word = event.target.innerText;
            defineWord(word);
        });
    }

    function defineWord(word) {
        var httpRequest = new XMLHttpRequest();
        if (!httpRequest) {
            alert('Cannot create an XMLHTTP instance');
            return false;
        }

        httpRequest.onreadystatechange = function () {

            if (httpRequest.readyState === XMLHttpRequest.DONE) {
                if (httpRequest.status === 200) {
                    var response = JSON.parse(httpRequest.responseText);
                    alert(response[0].eng[0]);
                }
                else {
                    alert('Not in dictionary');
                }
            }
        };
        httpRequest.open('GET', '/dict/' + word);
        httpRequest.send();

    }

}
setupTranslations();



