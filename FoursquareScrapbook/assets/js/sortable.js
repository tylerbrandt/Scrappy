// make a table sortable
var elem, sibs, pos, hideSelector;

$('.form tbody').sortable({
    /*containment: 'parent',
    zindex: 10, */
    items: 'tr',
    handle: 'td.sort_handle',
    update: function() {
        $(this).find('tr').each(function(i) {
            //if ($(this).find('input[id$=name]').val()) {
                $(this).find('input[id$=ORDER]').val(i+1);
            //}
        });
    }
});

$('td.sort_handle').css('cursor', 'move');
elem = $('.form input[id$=ORDER]').first().parents('td'); 
sibs = $(elem).parents('tr').find('td');
pos = parseInt(sibs.index(elem));
if(pos !== -1) {
    hideSelector = '.form td:nth-child(' + (pos+1) +'), .form th:nth-child(' + (pos+1) + ')';
    $(hideSelector).hide();    
}
