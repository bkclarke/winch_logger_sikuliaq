// datatables-core.js
window.initFixedHeaderTable = function (selector, options = {}) {
    const navbarHeight = $('.navbar').outerHeight() || 0;

    const defaultOptions = {
        responsive: true,
        scrollX: true,
        fixedHeader: {
            header: true,
            headerOffset: navbarHeight
        }
    };

    const table = $(selector).DataTable(
        $.extend(true, {}, defaultOptions, options)
    );

    // Update headerOffset on window resize
    $(window).on('resize', function () {
        table.fixedHeader.headerOffset($('.navbar').outerHeight() || 0);
    });

    return table;
};

