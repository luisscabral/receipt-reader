var receiptRequest = new XMLHttpRequest();
receiptRequest.open('GET', 'templates/edit.hmtl');

// function submit()



// var receipt = {
//     "name": ,
//     "head": ,
//     "total": ,
//     "date": ,
//     "date_created": ,
//     "category": ,
//     "language":
// }

// $(function() {
//     $.ajax({
        
//     })
// })





function runFunctions(input) {
    readURL(input);
    pullfiles();
}

function readURL(input) {
    if (input.files && input.files[0]) {
        var reader = new FileReader();

        reader.onload = function (e) {
            $('#blah')
                .attr('src', e.target.result);
        };

        reader.readAsDataURL(input.files[0]);
    }
}

var pullfiles=function(){ 
    // love the query selector
    var fileInput = document.querySelector("receipt-image");
    var files = fileInput.files;
    // cache files.length 
    var fl = files.length;
    var i = 0;

    while ( i < fl) {
        // localize file var in the loop
        var file = files[i];
        alert(file.name);
        i++;
    }    
}

// var file = document.getElementById('receipt-image').files[0];