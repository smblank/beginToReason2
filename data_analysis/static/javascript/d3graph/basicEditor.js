    // RESOLVE mode
    let ResolveMode = ace.require("ace/mode/resolve").Mode;

    // Basic editor settings
    aceEditor = ace.edit("editor")
    aceEditor.setTheme("ace/theme/chaos")
    fontSize = 16
    aceEditor.setFontSize(fontSize)
    editorContent = graph.lesson.code.replace(/\\r\\n/g, "\n")
    aceEditor.session.setValue(editorContent)
    aceEditor.getSession().setMode(new ResolveMode())
    aceEditor.setReadOnly(true)
    for(let index of graph.lesson.confirms) {
        aceEditor.session.addGutterDecoration(index, "ace_correct")
    }