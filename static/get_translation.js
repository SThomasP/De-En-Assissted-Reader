$('.word').on('click', function (event) {
    var e = event.target;
    var data = e.dataset;
    data.word = e.textContent;
    $.ajax({
        url: "/dict",
        type: 'POST',
        data: data,
        success: function (result) {
            popupEntry(result);
        }
    });
});

function popupEntry(entry) {
    var entryList = document.getElementById("dict-entries");
    entryList.insertAdjacentHTML('beforeend', entry);

}


function removeEntry(event) {
    var entryToDelete = event.target.parentNode.parentNode;
    var parent = entryToDelete.parentNode;
    parent.removeChild(entryToDelete);

}





