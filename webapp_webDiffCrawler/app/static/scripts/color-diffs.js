// let oldcontent = '{{ notification["oldcontent"] | replace("\n", "\\n") | replace("\r", "") }}';
let oldcontent = '{{ notification["oldcontent"] | safe }}';


// let currcontent = '{{ notification["currcontent"] | replace("\n", "\\n") | replace("\r", "")}}`;
let currcontent = '{{ notification["currcontent"] | safe }}';

let changes = JSON.parse('{{ notification["changes"] | safe }}');


console.log(changes);

// Escape \n
//currcontent = currcontent.replace(/\n/g, "\\n");
//oldcontent = oldcontent.replace(/\n/g, "\\n");

console.log("oldcontent = " + oldcontent);
console.log("currcontent = " + currcontent);


let oldcontentOffset = 0;
let currcontentOffset = 0;

let colors = {};
colors["green"] = {};
colors["green"]["before"] = '<span style="background-color: green">';
colors["green"]["after"] = '</span>';
colors["red"] = {};
colors["red"]["before"] = '<span style="background-color: red">';
colors["red"]["after"] = '</span>';
colors["yellow"] = {};
colors["yellow"]["before"] = '<span style="background-color: yellow">';
colors["yellow"]["after"] = '</span>';

// Mark the changes by coloring text
/*
for (let i = 0; i < changes.length; ++i) {
    // Every change returned from difflib is a 5-tuple
    let currChange = changes[i];
    let tag = currChange[0];
    let i1 = currChange[1];
    let i2 = currChange[2];
    let j1 = currChange[3];
    let j2 = currChange[4];

    if (tag === "replace") {
        // Yellow for the newly replaced current content
        let leftCurrcontent = currcontent.slice(0, currcontentOffset + j1);
        let rightCurrcontent = currcontent.slice(currcontentOffset + j2);
        let centerCurrcontent = currcontent.slice(currcontentOffset + j1, currcontentOffset + j2);

        currcontent = leftCurrcontent + colors["yellow"]["before"]
            + centerCurrcontent + colors["yellow"]["after"] + rightCurrcontent;
        currcontentOffset += colors["yellow"]["before"].length + colors["yellow"]["after"].length;

        // Yellow for the old content that has been replaced
        let leftOldcontent = oldcontent.slice(0, oldcontentOffset + i1);
        let rightOldcontent = oldcontent.slice(oldcontentOffset + i2);
        let centerOldcontent = oldcontent.slice(oldcontentOffset + i1, oldcontentOffset + i2);

        oldcontent = leftOldcontent + colors["yellow"]["before"]
            + centerOldcontent + colors["yellow"]["after"] + rightOldcontent;
        oldcontentOffset += colors["yellow"]["before"].length + colors["yellow"]["after"].length;

    } else if (tag === "insert") {
        // Green for the newly added current content
        let leftCurrcontent = currcontent.slice(0, currcontentOffset + j1);
        let rightCurrcontent = currcontent.slice(currcontentOffset + j2 );
        let centerCurrcontent = currcontent.slice(currcontentOffset + j1, currcontentOffset + j2);

        currcontent = leftCurrcontent + colors["green"]["before"]
            + centerCurrcontent + colors["green"]["after"] + rightCurrcontent;
        currcontentOffset += colors["green"]["before"].length + colors["green"]["after"].length;

    } else if (tag === "delete") {
        // Red for the removed, unreplaced old content
        let leftOldcontent = oldcontent.slice(0, oldcontentOffset + i1);
        let rightOldcontent = oldcontent.slice(oldcontentOffset + i2);
        let centerOldcontent = oldcontent.slice(oldcontentOffset + i1, oldcontentOffset + i2);

        oldcontent = leftOldcontent + colors["red"]["before"]
            + centerOldcontent + colors["red"]["after"] + rightOldcontent;
        oldcontentOffset += colors["red"]["before"].length + colors["red"]["after"].length;
    }
}
*/

// currcontent = currcontent.replace(/\r?\n/g, "<br />");


let newContentContainer = document.getElementById('new-content');
newContentContainer.innerHTML = '<p>' + currcontent + '</p>';

let oldContentContainer = document.getElementById('old-content');
oldContentContainer.innerHTML = '<p>' + oldcontent + '</p>';


/*
$(document).ready(function(){
        $("#new-content").text(currcontent);
        $("#old-content").text(oldcontent);
});
*/