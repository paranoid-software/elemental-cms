import {Plugster} from 'https://cdn.jsdelivr.net/gh/paranoid-software/plugster@1.0.12/dist/plugster.min.js';

class HtmlEditor extends Plugster {

    constructor(outlets) {
        super(outlets);
    };

    afterInit() {
        let self = this;
        self.editor = ace.edit(this._.editor.attr('id'));
        self.editor.setTheme("ace/theme/monokai");
        self.editor.session.setMode("ace/mode/html");
    }

    setPageSpec(value) {
        let self = this;
        let content = html_beautify(value.content, {
            "indent_size": "4",
            "indent_char": " ",
            "max_preserve_newlines": "5",
            "preserve_newlines": true,
            "keep_array_indentation": false,
            "break_chained_methods": false,
            "indent_scripts": "normal",
            "brace_style": "collapse",
            "space_before_conditional": true,
            "unescape_strings": false,
            "jslint_happy": false,
            "end_with_newline": false,
            "wrap_line_length": "0",
            "indent_inner_html": true,
            "comma_first": false,
            "e4x": false,
            "indent_empty_lines": false
        });
        self.editor.session.setValue(content);
    }

}

let htmlEditor = new HtmlEditor({
    editor: {}
});

htmlEditor.init().then((me) => {
    Plugster.plug(me);
});

export {htmlEditor as HtmlEditor}
