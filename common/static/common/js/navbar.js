// common/static/common/js/navbar.js
document.addEventListener('DOMContentLoaded', () => {
    // notificationを閉じる処理
    const $deleteButtons = document.querySelectorAll('.notification > .delete');
    $deleteButtons.forEach($el => {
        $el.addEventListener('click', () => {
            $el.parentElement.classList.add('is-hidden');
        });
    });

    // navbar-burgerの処理
    const $navbarBurgers = Array.prototype.slice.call(document.querySelectorAll('.navbar-burger'), 0);
    if ($navbarBurgers.length > 0) {
        $navbarBurgers.forEach(el => {
            el.addEventListener('click', () => {
                const target = el.dataset.target;
                const $target = document.getElementById(target);
                el.classList.toggle('is-active');
                $target.classList.toggle('is-active');
            });
        });
    }
});

// // notificationを×押下で閉じれるように。
// for (const element of document.querySelectorAll('.notification > .delete')) {
//     element.addEventListener('click', e => {
//         e.target.parentElement.classList.add('is-hidden');
//     });
// }
// // navbar-burgerのボタン処理。https://bulma.io/documentation/components/navbar/
// document.addEventListener('DOMContentLoaded', () => {
//     // Get all "navbar-burger" elements
//     const $navbarBurgers = Array.prototype.slice.call(document.querySelectorAll('.navbar-burger'), 0);
//     // Check if there are any navbar burgers
//     if ($navbarBurgers.length > 0) {
//         // Add a click event on each of them
//         $navbarBurgers.forEach( el => {
//             el.addEventListener('click', () => {
//                 // Get the target from the "data-target" attribute
//                 const target = el.dataset.target;
//                 const $target = document.getElementById(target);
//                 // Toggle the "is-active" class on both the "navbar-burger" and the "navbar-menu"
//                 el.classList.toggle('is-active');
//                 $target.classList.toggle('is-active');
//             });
//         });
//     }
// });