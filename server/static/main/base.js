$(document).ready(function() {
    $('[class*="original-post-"]').on("mouseenter", function() {
        $(this).find('[class^="post-actions-"]').addClass('show')
    }).on("mouseleave", function() {
        $(this).find('[class^="post-actions-"]').removeClass('show')
    });
});
