
/*!
 * datatables init for use in tables with fixed header
 * uses dynamic navbarHeight const to determmine offset from top of page
 */
$(function () {

    $('.dt-fixed').each(function () {
        const $table = $(this);

        // Add shared classes
        $table.addClass('display nowrap table table-striped table-bordered');

        // Style thead consistently
        $table.find('thead').addClass('thead-light');

        const navbarHeight = $('.navbar').outerHeight() || 0;

        const table = $table.DataTable({
            responsive: true,
            scrollX: true,
            order: [[0, 'desc']],
            fixedHeader: {
                header: true,
                headerOffset: navbarHeight
            }
        });

        $(window).on('resize', function () {
            table.fixedHeader.headerOffset(
                $('.navbar').outerHeight() || 0
            );
        });
    });
});

