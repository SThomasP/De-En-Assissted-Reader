
function setupTranslations() {
    var words = document.getElementsByClassName('word');
    for (var i = 0; i < words.length; i++) {
        words[i].addEventListener('click', function (event) {
            var word = event.target.innerText;
            // commented out while writing and testing display code.
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
                    var response = httpRequest.responseText;
                    popupEntry(response);
                }
                else {
                    alert('Not in dictionary');
                }
            }
        };
        httpRequest.open('GET', '/dict/html/' + word);
        httpRequest.send();


    }
}

function removeEntry(event) {
    var entryToDelete = event.target.parentNode.parentNode;
    var parent = entryToDelete.parentNode;
    parent.removeChild(entryToDelete);

}

function popupEntry(entry) {
    var entryList = document.getElementById("dict-entries");
    entryList.insertAdjacentHTML('beforeend',entry);

}


setupTranslations();



