$(document).ready(function() {
    
    $('.share-btn').on('click', function() {
        var blogId = $(this).data('blog-id');
        var directLink = window.location.href + '#' + blogId;
        alert('Copy this link to share:\n' + directLink);
    });

});
