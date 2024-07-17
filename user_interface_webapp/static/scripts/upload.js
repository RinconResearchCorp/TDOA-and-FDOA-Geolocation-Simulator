// javascript is CASE SENSITIVE */
// file to implement functionality to upload html file when it renders webapge 
// js below is to render animation to the upload and submit buttons 
// also  displays the file name once a file has been attached.

(function() {
    var resize;

    $("div").click(function() {
        if ($("div").hasClass("loading-start")) {
            if ($("div").hasClass("loading-end")) {
                return $("div").removeClass(); 
            }
        } else {
            setTimeout(function() {     /* sets the timeout */
                $("div").addClass("loading-start");
            }, 0);

            setTimeout(function() {
                $("div").addClass("loading-progress");
            }, 500);

            setTimeout(function() {
                $("div").addClass("loading-end");
            }, 1500);
        }
    });

    resize = function() {
        $("body").css({
            "margin-top": ~~((window.innerHeight - 260) / 2) + "px"
        });
    };

    $(window).resize(resize);
    resize();
}).call(this);

// file name display on the upload page
$(document).ready(function() {
    $('#fileUpload').change(function() {
        var fileInput = $(this)[0].files[0]; //  file object
        var filename = fileInput.name; // file name
        var filetype = fileInput.type; //file type

        $('#fileUploadName').text('Selected File: ' + filename); //display the file name
        $('#fileUploadType').text('File Type: ' + filetype); // display the file type
    });
});
