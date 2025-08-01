document.addEventListener('DOMContentLoaded', () => {
    // Basic fade-in for the body once everything is loaded
    document.body.classList.add('loaded');

    // Function to add 'animated' class when element is in viewport
    const animateOnScroll = (entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animated');
                observer.unobserve(entry.target); // Stop observing once animated
            }
        });
    };

    // Create an Intersection Observer instance
    const observer = new IntersectionObserver(animateOnScroll, {
        root: null, // viewport as root
        rootMargin: '0px',
        threshold: 0.1 // Trigger when 10% of the element is visible
    });

    // Observe all elements with animation classes
    document.querySelectorAll('.animate-fade-in, .animate-fade-in-up, .animate-slide-in-left, .animate-slide-in-right, .uk-animation-slide-bottom-small').forEach(element => {
        observer.observe(element);
    });
});