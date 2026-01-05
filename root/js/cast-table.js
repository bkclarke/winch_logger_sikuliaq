// cast-table.js
$(function() {

    const isSuperUser =
    $('#cast-table-container').data('superuser') === true ||
    $('#cast-table-container').data('superuser') === 'true';

    /* -------------------------------
       Tooltips
    -------------------------------- */
    $('[data-toggle="tooltip"]').tooltip();

    /* -------------------------------
       Navigation buttons
    -------------------------------- */
    $('#castmanualenter').on('click', function () {
        window.location.href = "{% url 'castmanualenter' %}";
    });

    $('#caststartend').on('click', function () {
        window.location.href = "{% url 'caststartend' %}";
    });

    /* -------------------------------
       Delete modal + permissions
    -------------------------------- */
    const deleteModal = new bootstrap.Modal(
        document.getElementById('deleteConfirmModal')
    );

    $('.delete-button').on('click', function () {
        const isSuperUser = '{{ user.is_superuser|yesno:"true,false" }}' === 'true';
        if (!isSuperUser) {
            alert('You must be logged in as an admin to delete this cast.');
            return;
        }
        $('#deleteForm').attr('action', $(this).data('url'));
        deleteModal.show();
    });

    $('.edit-button').on('click', function (e) {
        const isSuperUser = '{{ user.is_superuser|yesno:"true,false" }}' === 'true';
        if (!isSuperUser) {
            e.preventDefault();
            alert('You must be logged in as an admin to edit this cast.');
        }
    });

    /* -------------------------------
       Initialize DataTable via datatables-core
    -------------------------------- */
    window.castDataTable = window.initFixedHeaderTable('#table', {
        order: [[1, 'desc']],
        initComplete: function () {
            $('#cast-table-container').css('opacity', 1);
        }
    });

    /* -------------------------------
       CSV Download utility
    -------------------------------- */
    function downloadCSV(filename, csvContent) {
        const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
        const link = document.createElement('a');
        link.href = URL.createObjectURL(blob);
        link.download = filename;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    }

    function getVisibleRowsData(selectedColumns = null) {
        const rows = $('#table tbody tr:visible');
        if (rows.length === 0) return null;

        let csv = [];

        // Headers
        let headers = [];
        $('#table thead th').each(function (i) {
            if (!selectedColumns || selectedColumns.includes(i)) {
                headers.push($(this).text().trim());
            }
        });
        csv.push(headers.join(','));

        // Rows
        rows.each(function () {
            let rowData = [];
            $(this).find('td').each(function (i) {
                if (!selectedColumns || selectedColumns.includes(i)) {
                    rowData.push($(this).text().trim());
                }
            });
            csv.push(rowData.join(','));
        });

        return csv.join('\n');
    }

    /* -------------------------------
       Download filtered table
    -------------------------------- */
    $('#tableButton').on('click', function () {
        const csvContent = getVisibleRowsData();
        if (!csvContent) return alert('No data to download.');
        downloadCSV('filtered_cast_table.csv', csvContent);
    });

    /* -------------------------------
       UNOLS report download
    -------------------------------- */
    $('#unolsButton').on('click', function () {
        const selectedColumns = [1,3,18,4,5,8,9,10,23,11,15,20,21,22];
        const rows = $('#table tbody tr:visible');
        if (rows.length === 0) return alert('No data to download.');

        const csvContent = getVisibleRowsData(selectedColumns);

        // UNOLS headers
        const unolsHeader = [
            '#UNOLS TENSION MEMBER REPORT',
            '#Casts: ' + rows.length,
            '#'
        ];

        downloadCSV('UNOLS_report.csv', unolsHeader.join('\n') + '\n' + csvContent);
    });

});


