function login_auth() {
  $.ajax({
    type: "GET",
    url: "/auth_login",
    data: {},
    success: function (response) {
      let currentUrl = window.location.pathname; // Mendapatkan URL saat ini
      let temp_navbar = "";

      if (response["result"] == "success") {
        if (response.data.level == "1") {
          temp_navbar = `
          <ul>
            <li><a href="/" id="navhome" class="${currentUrl === '/' ? 'active' : ''}">Home</a></li>
            <li><a href="/shop" id="navcontent" class="${currentUrl === '/shop' ? 'active' : ''}">Shop</a></li>
            <li><a href="/contact" id="navmedia" class="${currentUrl === '/contact' ? 'active' : ''}">Contact</a></li>
            <li><a href="/about" id="navabout" class="${currentUrl === '/about' ? 'active' : ''}">About Us</a></li>
          </ul>`;
        } else if (response.data.level == "2") {
          console.log(response.data);
          let unread = "";
          if (response.notif > 0) {
            unread = `&nbsp;<i class="bi bi-circle-fill text-danger"></i>`;
          }
          temp_navbar = `
          <ul>
            <li><a href="/" id="navhome" class="${currentUrl === '/' ? 'active' : ''}">Beranda</a></li>
            <li><a href="/shop" id="navcontent" class="${currentUrl === '/shop' ? 'active' : ''}">Produk</a></li>
            <li><a href="/contact" id="navmedia" class="${currentUrl === '/contact' ? 'active' : ''}">Contact</a></li>
            <li><a href="/layanan" id="navcontent" class="${currentUrl === '/layanan' ? 'active' : ''}">Layanan</a></li>
            <li class="nav-item dropdown">
              <a class="nav-link dropdown-toggle ${['/blog', '/portofolio'].includes(currentUrl) ? 'active' : ''}" href="#" id="blogDropdown" role="button" data-bs-toggle="dropdown" aria-expanded="false">
                Blog
              </a>
              <ul class="dropdown-menu" aria-labelledby="blogDropdown">
                <li><a class="dropdown-item ${currentUrl === '/blog' ? 'active' : ''}" href="/blog">Blog</a></li>
                <li><a class="dropdown-item ${currentUrl === '/portofolio' ? 'active' : ''}" href="/portofolio">Portofolio</a></li>
              </ul>
            </li>
            <li>
              <a class="nav-link ${currentUrl === '/cart' ? 'active' : ''}" href="/cart">
                <i class="bi bi-cart-fill" style="font-size: 1.2rem;"></i>
              </a>
            </li>
            <li class="nav-item">
              <a class="nav-link ${currentUrl === '/orders' ? 'active' : ''}" href="/orders">Orders</a>
            </li>
            <li><a href="/user/${response.data.username}" id="navmedia" class="${currentUrl === '/user/' + response.data.username ? 'active' : ''}">Profil</a></li>
            <li><a href="/about" id="navabout" class="${currentUrl === '/about' ? 'active' : ''}">Tentang Kami</a></li>
            <li>
              <a onclick="sign_out()" style="cursor: pointer" id="navlogout" class="">
                Logout&nbsp;&nbsp;
                <img class="rounded-circle shadow-1-strong me-3" src="/static/${response.data.profile_icon}" alt="avatar" width="30" height="30" />
              </a>
            </li>
          </ul>`;
        }
      } else {
        temp_navbar = `
        <ul>
          <li><a href="/" id="navhome" class="${currentUrl === '/' ? 'active' : ''}">Beranda</a></li>
          <li><a href="/shop" id="navcontent" class="${currentUrl === '/shop' ? 'active' : ''}">Produk</a></li>
          <li><a href="/layanan" id="navcontent" class="${currentUrl === '/layanan' ? 'active' : ''}">Layanan</a></li>
          <li class="nav-item dropdown">
            <a class="nav-link dropdown-toggle ${['/blog', '/portofolio'].includes(currentUrl) ? 'active' : ''}" href="#" id="blogDropdown" role="button" data-bs-toggle="dropdown" aria-expanded="false">
              Blog
            </a>
            <ul class="dropdown-menu" aria-labelledby="blogDropdown">
              <li><a class="dropdown-item ${currentUrl === '/blog' ? 'active' : ''}" href="/blog">Blog</a></li>
              <li><a class="dropdown-item ${currentUrl === '/portofolio' ? 'active' : ''}" href="/portofolio">Portofolio</a></li>
            </ul>
          </li>
          <li><a href="/contact" id="navmedia" class="${currentUrl === '/contact' ? 'active' : ''}">Kontak</a></li>
          <li><a href="/about" id="navabout" class="${currentUrl === '/about' ? 'active' : ''}">Tentang Kami</a></li>
          <li><a href="/login" id="navlogin">Login</a></li>
        </ul>`;
      }

      // Memasukkan navbar ke dalam elemen dengan id 'navbar'
      $("#navbar").html(temp_navbar);
    },
  });
  $(document).on("click", ".navbar .dropdown > a", function (e) {
    e.preventDefault(); // Mencegah navigasi default
    let parent = $(this).parent();
  
    // Menutup dropdown lainnya jika ada yang terbuka
    $(".navbar .dropdown").not(parent).removeClass("dropdown-active");
  
    // Toggle dropdown
    parent.toggleClass("dropdown-active");
  });
  
}

login_auth();
