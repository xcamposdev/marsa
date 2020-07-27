odoo.define('calculator_custom.calculator_javscript', function (require) {
'use strict';

var FieldMany2One = require('web.relational_fields').FieldMany2One;
var FieldRegistry = require('web.field_registry');

var calculadora_field = FieldMany2One.extend({
    events: _.extend({}, FieldMany2One.prototype.events, {
        'click .o_external_button': '_onCalculatorButtonClick'
    }),

    _onCalculatorButtonClick: function (event) {
        event.preventDefault();
        event.stopPropagation();
        this.attrs.context = "{'from_button': True }";
        this.trigger_up('field_changed',{ 
            dataPointID: this.dataPointID, 
            changes: this.lastChangeEvent.data.changes
        });
    }
});
FieldRegistry.add('custom_calculator_many2one', calculadora_field);
return calculadora_field;
});