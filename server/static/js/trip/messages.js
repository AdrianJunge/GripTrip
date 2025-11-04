$(function() {
    const $replyPreview  = $('#reply-preview');
    const $previewUser   = $('#reply-preview-user');
    const $previewContent= $('#reply-preview-content');
    const $responseToInput = $('#response_to');
    const $messageInput  = $('#message-input');

    $('.reply-btn').on('click', function () {
        const $btn = $(this);
        const id      = $btn.attr('data-reply-id');
        const author  = $btn.attr('data-reply-author');
        const content = $btn.attr('data-reply-content');

        $responseToInput.val(id);
        $previewUser.text('@' + author);
        $previewContent.text(content);
        $replyPreview.css('display', 'flex');

        $messageInput.focus();
    });

    $(document).on('click', '.reply-btn', function () {
        const $btn = $(this);
        const id      = $btn.data('reply-id');
        const author  = $btn.data('reply-author');
        const content = $btn.data('reply-content');

        $responseToInput.val(id || '');
        $previewUser.text(author ? ('@' + author) : '');
        $previewContent.text(content || '');
        $replyPreview.show().css('display', 'flex');
        $messageInput.focus();
    });

    $('#reply-cancel').on('click', function () {
        $responseToInput.val('');
        $previewUser.text('');
        $previewContent.text('');
        $replyPreview.hide();
    });

    $('#message-form').on('submit', function (e) {
        e.preventDefault();
        alert('Post message: to be implemented');
    });
});
