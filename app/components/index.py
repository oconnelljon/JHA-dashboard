index_string = """
<!DOCTYPE html>
<html>
    <head>
        <link href="css/01common.css" rel="stylesheet" type="text/css" media="screen" />
        <link href="css/02custom.css" rel="stylesheet" type="text/css" media="screen" />
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <!-- Google Tag Manager -->
        <script>(function (w, d, s, l, i) {
            w[l] = w[l] || []; w[l].push({
                'gtm.start':
                new Date().getTime(), event: 'gtm.js'
            }); var f = d.getElementsByTagName(s)[0],
                j = d.createElement(s), dl = l != 'dataLayer' ? '&l=' + l : ''; j.async = true; j.src =
                'https://www.googletagmanager.com/gtm.js?id=' + i + dl; f.parentNode.insertBefore(j, f);
            })(window, document, 'script', 'dataLayer', 'GTM-TKQR8KP');</script>
        <!-- End Google Tag Manager -->
        <script type="text/javascript" src="/uswds/dist/js/uswds-init.min.js"></script>
        <link rel="stylesheet" href="/uswds/dist/css/uswds.min.css" />
    </head>
    <body>
        <script src="/uswds/dist/js/uswds.min.js"></script>
        <header id="navbar" class="header-nav" role="banner">
        <div class="tmp-container">
            <!-- primary navigation bar -->
            <!-- search bar-->
            <div class="header-search">
            <a class="logo-header" href="https://www.usgs.gov/" title="Home">
                <img class="img" src="assets/img/logo.png" alt="Home" />
            </a>
            <form action="https://www.usgs.gov/science-explorer-results" method="GET" id="search-box">
                <div class="fa-wrapper"><label for="se_search" class="only">Search</label>
                <input id="se_search" type="search" name="es" placeholder="Search">
                <button class="fa fa-search" type="submit">
                    <span class="only">Search</span>
                </button>
                </div>
            </form>
            </div>
            <!-- end search bar-->
        </div>
        <!-- end header-container-->
        </header>
        {%app_entry%}
        <footer class="footer">
            {%config%}
            {%scripts%}
            {%renderer%}
            <!-- USGS Footer -->
            <div class="tmp-container">
                <!-- .footer-wrap -->
                    <!-- .footer-doi -->
                    <div class="footer-doi">
                        <!-- footer nav links -->
                        <ul class="menu nav">
                            <li class="first leaf menu-links menu-level-1"><a href="https://www.doi.gov/privacy">DOI Privacy Policy</a></li>
                            <li class="leaf menu-links menu-level-1"><a href="https://www.usgs.gov/policies-and-notices">Legal</a></li>
                            <li class="leaf menu-links menu-level-1"><a href="https://www.usgs.gov/accessibility-and-us-geological-survey">Accessibility</a></li>
                            <li class="leaf menu-links menu-level-1"><a href="https://www.usgs.gov/sitemap">Site Map</a></li>
                            <li class="last leaf menu-links menu-level-1"><a href="https://answers.usgs.gov/">Contact USGS</a></li>
                        </ul>
                        <!--/ footer nav links -->      
                    </div>
                    <!-- /.footer-doi -->

                    <!-- <hr> -->

                <!-- .footer-utl-links -->
                <div class="footer-doi">
                    <ul class="menu nav">
                        <li class="first leaf menu-links menu-level-1"><a href="https://www.doi.gov/">U.S. Department of the Interior</a></li>
                        <li class="leaf menu-links menu-level-1"><a href="https://www.doioig.gov/">DOI Inspector General</a></li>
                        <li class="leaf menu-links menu-level-1"><a href="https://www.whitehouse.gov/">White House</a></li>
                        <li class="leaf menu-links menu-level-1"><a href="https://www.whitehouse.gov/omb/management/egov/">E-gov</a></li>
                        <li class="leaf menu-links menu-level-1"><a href="https://www.doi.gov/pmb/eeo/no-fear-act">No Fear Act</a></li>
                        <li class="last leaf menu-links menu-level-1"><a href="https://www.usgs.gov/about/organization/science-support/foia">FOIA</a></li>
                    </ul>
                    </div>			
                <!-- /.footer-utl-links -->
                <!-- .footer-social-links -->
                <div class="footer-social-links">
                    <ul class="social">
                        <li class="follow">Follow</li>
                        <li class="twitter">
                            <a href="https://twitter.com/usgs" target="_blank">
                                <i class="fa fa-twitter-square"><span class="only">Twitter</span></i>
                            </a>
                        </li>
                        <li class="facebook">
                            <a href="https://facebook.com/usgeologicalsurvey" target="_blank">
                                <i class="fa fa-facebook-square"><span class="only">Facebook</span></i>
                            </a>
                        </li>
                        <li class="github">
                            <a href="https://github.com/usgs" target="_blank">
                                <i class="fa fa-github"><span class="only">GitHub</span></i>
                            </a>
                        </li>
                        <li class="flickr">
                            <a href="https://flickr.com/usgeologicalsurvey" target="_blank">
                                <i class="fa fa-flickr"><span class="only">Flickr</span></i>
                            </a>
                        </li>
                        <li class="youtube">
                            <a href="http://youtube.com/usgs" target="_blank">
                                <i class="fa fa-youtube-play"><span class="only">YouTube</span></i>
                            </a>
                        </li>
                        <li class="instagram">
                            <a href="https://instagram.com/usgs" target="_blank">
                                <i class="fa fa-instagram"><span class="only">Instagram</span></i>
                            </a>
                        </li>
                    </ul>
                </div>
                <!-- /.footer-social-links -->
            </div>
                <!-- /.footer-wrap -->	
        </footer>
        <!-- Google Tag Manager (noscript) -->
        <noscript><iframe src="https://www.googletagmanager.com/ns.html?id=GTM-TKQR8KP"
        height="0" width="0" style="display:none;visibility:hidden"></iframe></noscript>
        <!-- End Google Tag Manager (noscript) -->
    </body>
</html>
"""
