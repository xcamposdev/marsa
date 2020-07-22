odoo.define('calculator_custom.calculator_javscript', function (require) {
'use strict';

//var Model = require('web.Model');
var rpc = require('web.rpc');
var FieldMany2One = require('web.relational_fields').FieldMany2One;
var FieldRegistry = require('web.field_registry');

var calculadora_field = FieldMany2One.extend({
    events: _.extend({}, FieldMany2One.prototype.events, {
        'click .o_external_button': '_onCalculatorButtonClick'
    }),

    _onCalculatorButtonClick: function (event) {
        event.preventDefault();
        event.stopPropagation();
        var self = this;
        console.log(self);
        console.log(event);
        // self.trigger_up('field_changed', {
        //     dataPointID: self.dataPointId,
        //     changes: { product_id: { id: self.value.data.id } }
        //     //changes: { product_id: {id: result.product_id}, },
        // });
        // console.log(event);
        // console.log(this);
        // var context = this.record.getContext(this.recordParams);
        //return rpc.query({
        this._rpc({
                model: 'sale.order',
                method: 'button_add_data',
                context: this.record.getContext(this.recordParams),
                //args: [],
        });
            // }).then(function(result){
            //     console.log(result);
            //     //self._render();
            // });
            // _onSelectionChange: function () {
            //     var value = this.$('select').val();
            //     this.reinitialize(false);
            //     this._setRelation(value);
            // },
    }
});
FieldRegistry.add('custom_calculator_many2one', calculadora_field);
return calculadora_field;
});