// dummy entry for testing display code, currently: Sahne
var dummy_entry = JSON.parse("{\"category\": \"noun\", \"grammar\": [{\"Gender\": \"Feminine\", \"Case\": \"Dative\", \"Number\": \"Singular\"}, {\"Gender\": \"Feminine\", \"Case\": \"Genitive\", \"Number\": \"Singular\"}, {\"Gender\": \"Feminine\", \"Case\": \"Accusative\", \"Number\": \"Singular\"}], \"de\": \"Sahne\", \"en\": [\"cream\"], \"root\": \"Sahne\"}");

function setupTranslations() {
    var words = document.getElementsByClassName('word');
    for (var i = 0; i < words.length; i++) {
        words[i].addEventListener('click', function (event) {
            var word = event.target.innerText;
            popUpEntry(dummy_entry);

            // commented out while writing and testing display code.
            // defineWord(word);
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
                    popUpEntry(response);
                }
                else {
                    alert('Not in dictionary');
                }
            }
        };
        httpRequest.open('GET', '/dict/' + word);
        httpRequest.send();


    }

    function popUpEntry(entry) {
    }

}
setupTranslations();



