/**
 * Helper for sending request to get matches for the document.
 *
 * @param stem - Stem string that is supposed to be matched in the document.
 */
function get_matches(stem) {
    var current_url = window.location.href;
    var last_slash_index = current_url.lastIndexOf("/");
    var last_question_index = current_url.lastIndexOf("?");

    var base = current_url.substring(0, last_slash_index) + "/match";
    var params = current_url.substring(last_question_index) + "&stem=" + stem;
    window.location.href = base + params;
}
