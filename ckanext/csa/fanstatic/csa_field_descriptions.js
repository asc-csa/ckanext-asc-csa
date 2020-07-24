"use strict";

/* csa_field_descriptions
 *
 * This JavaScript module adds a Bootstrap popover with the hover trigger on
 * dataset fields in the additional_info.html page
 * 
 * This should be changed to a button interface to reach accessibility requirements
 *
 * field_name - the name of the metadata field which a definition is needed
 * 
 * Most of this can be read up on at the following documentation
 * https://docs.ckan.org/en/2.8/theming/javascript.html
 */
ckan.module('csa_field_descriptions', function ($) {
  return {
    initialize: function () {
      $.proxyAll(this, /_on/);
      // on hover, (Should probably be changed to a clickable interface to meet accessibility reqs)
      // button should also have a text-based alt-text that should describe the button for screen readers
      this.el.on('click', this._onClick);

      this.sandbox.subscribe('dataset_popover_clicked',
                              this._onPopoverClicked);

    },
                            
      teardown: function() {
        this.sandbox.unsubscribe('dataset_popover_clicked',
                                    this._onPopoverClicked);
      },






    _snippetReceived: false,

    _onClick: function(event) {
        if (!this._snippetReceived) {
            this.sandbox.client.getTemplate('csa_field_descriptions.html',
                                            this.options,
                                            this._onReceiveSnippet);
            this._snippetReceived = true;
        }
        
            this.sandbox.publish('dataset_popover_clicked', this.el);

    },

    _onPopoverClicked: function(button) {
      if (button != this.el) {
        this.el.popover('hide');
      }



    },

    _onReceiveSnippet: function(html) {
      // Create a bootstrap popover element passing the data and also the template
      this.el.popover('destroy');
      this.el.popover({title: this.options.field_name, html: true,
                       content: html, placement: 'left'});
      this.el.popover('show');
    },

   

  };
});