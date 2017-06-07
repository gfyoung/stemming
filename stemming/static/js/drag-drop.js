/**
 * Handler for drag-and-dropping files into the text field input.
 *
 * @param evt - The drag-and-drop event to handle.
 */
function handleFileSelect(evt) {
    evt.stopPropagation();
    evt.preventDefault();

    // FileList object.
    var files = evt.dataTransfer.files;
    var reader = new FileReader();

    reader.onload = function(event) {
        document.getElementById("document").value = event.target.result;
    };

    if (!files[0].name.endsWith(".txt")) {
        document.getElementById("document").value = "Sorry, only .txt files are accepted! Please try again.";
    } else {
        reader.readAsText(files[0], "UTF-8");
    }
}

/**
 * Handler for dragging the file into the text field input.
 *
 * @param evt - The drag over event to handle.
 */
function handleDragOver(evt) {
    evt.stopPropagation();
    evt.preventDefault();

    // Explicitly show this is a copy.
    evt.dataTransfer.dropEffect = "copy";
}

window.onload = function() {
    var drop_zone = document.getElementById("document");
    drop_zone.addEventListener("dragover", handleDragOver, false);
    drop_zone.addEventListener("drop", handleFileSelect, false);
};

