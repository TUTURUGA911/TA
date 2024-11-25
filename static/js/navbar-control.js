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
            <li><a href="/" id="navhome" class="${currentUrl === '/' ? 'active' : ''}">Home</a></li>
            <li><a href="/shop" id="navcontent" class="${currentUrl === '/shop' ? 'active' : ''}">Shop</a></li>
            <li><a href="/contact" id="navmedia" class="${currentUrl === '/contact' ? 'active' : ''}">Contact</a></li>
            <li><a href="/about" id="navabout" class="${currentUrl === '/about' ? 'active' : ''}">About Us</a></li>
            <li class="nav-item">
              <a class="nav-link ${currentUrl === '/cart' ? 'active' : ''}" href="/cart">
                <i class="bi bi-cart-fill" style="font-size: 1.2rem;"></i>
              </a>
            </li>
            <li class="nav-item">
              <a class="nav-link ${currentUrl === '/orders' ? 'active' : ''}" href="/orders">Orders</a>
            </li>
            <li><a href="/user/${response.data.username}" id="navmedia" class="${currentUrl === '/user/' + response.data.username ? 'active' : ''}">Profil</a></li>
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
          <li><a href="/produk" id="navcontent" class="${currentUrl === '/produk' ? 'active' : ''}">Produk</a></li>
          <li><a href="/layanan" id="navcontent" class="${currentUrl === '/layanan' ? 'active' : ''}">Layanan</a></li>
          <li><a href="/blog" id="navcontent" class="${currentUrl === '/blog' ? 'active' : ''}">Blog</a></li>
          <li><a href="/contact" id="navmedia" class="${currentUrl === '/contact' ? 'active' : ''}">Kontak</a></li>
          <li><a href="/about" id="navabout" class="${currentUrl === '/about' ? 'active' : ''}">Tentang Kami</a></li>
        </ul>`;
      }

      // Memasukkan navbar ke dalam elemen dengan id 'navbar'
      $("#navbar").html(temp_navbar);
    },
  });
}

login_auth();

// Fungsi logout tetap sama
function sign_out() {
  Swal.fire({
    title: "Are you sure?",
    text: "Anda akan logout dari akun anda",
    icon: "warning",
    showCancelButton: true,
    confirmButtonColor: "#3085d6",
    cancelButtonColor: "#d33",
    confirmButtonText: "Ya, logout!",
  }).then((result) => {
    if (result.isConfirmed) {
      $.removeCookie("mytoken", { path: "/" });
      Swal.fire({
        title: "Ter-logout!",
        text: "Anda sudah logout dari akun anda!",
        icon: "warning",
      }).then((result) => {
        if (result.isConfirmed) {
          window.location.href = "/login";
        }
      });
    }
  });
}
