$(document).ready(function() {
    var currentIndex = 0;
    var scrollAmount = $('.carousel-item').outerWidth(true); 

    var container = $('.carousel');

    function showItem(index) {
        var carouselItems = $('.carousel-item');
        carouselItems.removeClass('active');
        $(carouselItems[index]).addClass('active');
    }

    function nextItem() {
        var numItems = $('.carousel-item').length;
        currentIndex = (currentIndex + 1) % numItems;
        showItem(currentIndex);
    }

    function prevItem() {
        var numItems = $('.carousel-item').length;
        currentIndex = (currentIndex - 1 + numItems) % numItems;
        showItem(currentIndex);
    }

    function autoScroll() {
    var numItems = $('.carousel-item').length;
    currentIndex = (currentIndex + 1) % numItems;
    
    if (currentIndex === 0) {
        container.animate({
            scrollLeft: 0
        }, 1000, 'linear');
    } else {
        container.animate({
            scrollLeft: '+=' + scrollAmount
        }, 1000, 'linear');
    }
    showItem(currentIndex);
}

    
    
    $('.carousel-button[data-direction="prev"]').on('click', function() {
        container.stop().animate({
            scrollLeft: '-=' + scrollAmount
        }, 1000, 'linear', prevItem);
    });

    $('.carousel-button[data-direction="next"]').on('click', function() {
        container.stop().animate({
            scrollLeft: '+=' + scrollAmount
        }, 1000, 'linear', nextItem);
    });
    
    
    


    setInterval(autoScroll, 3000);

    showItem(currentIndex);
});
