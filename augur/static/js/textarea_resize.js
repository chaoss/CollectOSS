// Create auto-resizing for any textareas in the document
const tx = document.getElementsByTagName("textarea");

for (let i = 0; i < tx.length; i++) {
    tx[i].setAttribute("style", "height:" + (tx[i].scrollHeight) + "px;overflow-y:hidden;");
    tx[i].addEventListener("input", OnTextAreaInput, false);
}

function OnTextAreaInput() {
    this.style.height = "auto";
    this.style.height = (this.scrollHeight) + "px";
}
