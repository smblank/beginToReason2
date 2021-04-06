    // RESOLVE mode
    let ResolveMode = ace.require("ace/mode/resolve").Mode;

    // Basic editor settings
    aceEditor = ace.edit("editor");
    aceEditor.setTheme("ace/theme/chaos"); //chaos or solarized_light
    fontSize = 16;
    aceEditor.setFontSize(fontSize);

    // Store the content for future use
    editorContent = graph.lesson.code.replace(/\\r\\n/g, "\n")
    aceEditor.session.setValue(editorContent);

    aceEditor.getSession().setMode(new ResolveMode());
    aceEditor.setReadOnly(true)