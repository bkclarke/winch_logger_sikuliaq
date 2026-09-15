// js/delete-modal.js
$(function() {
    const deleteModalEl = document.getElementById('deleteConfirmModal');
    const feedbackModalEl = document.getElementById('feedbackModal');

    if (!deleteModalEl || !feedbackModalEl) return;

    const deleteModal = new bootstrap.Modal(deleteModalEl);
    const feedbackModal = new bootstrap.Modal(feedbackModalEl);

    const isSuperUser = window.WWDB_IS_SUPERUSER || false;

    // If you want to get the superuser flag from a data attribute:
    // const isSuperUser = $('#deleteConfirmModal').data('superuser') === true;

    $(document).on('click', '.delete-button', function () {
        if (!isSuperUser) {
            alert('You must be logged in as an admin to delete this wire.');
            return;
        }
        $('#deleteForm').attr('action', $(this).data('url'));
        deleteModal.show();
    });

    $('#deleteForm').on('submit', function(e) {
        e.preventDefault();

        const form = $(this);
        const url = form.attr('action');

        $.ajax({
            url: url,
            method: 'POST',
            data: form.serialize(),
            success: function() {
                deleteModal.hide();
                location.reload();
            },
            error: function(xhr) {
                deleteModal.hide();
                if (xhr.status === 400 || xhr.status === 403) {
                    feedbackModal.show();
                } else {
                    alert('An unexpected error occurred.');
                }
            }
        });
    });
});

