577
578
579
580
581
582
583
584
585
586
587
588
589
590
591
592
593
594
595
596
597
598
599
600
601
602
603
604
605
606
607
608
609
610
611
612
613
614
615
616
617
618
619
620
621
622
623
624
625
626
627
628
629
630
631
632
633
634
635
636
637
638
639
640
641
642
643
644
645
646
647
648
649
650
651
652
653
654
655
656
657
658
659
660
661
662
663
664
665
666
667
668
669
670
671
672
673
674
675
676
677
678
679
680
681
682
683
684
685
686
687
688
689
690
691
692
693
694
695
696
697
698
699
700
701
702
703
704
705
706
707
708
709
710
711
712
713
714
715
      };
      xhr.send();
    }

    function renderDashboard() {
      var root = document.getElementById("app-root");
      var navHtml = "";
      for (var i = 0; i < secciones.length; i++) {
        var s = secciones[i];
        var activeClass = (s.index === vistaActual) ? "nav-btn active" : "nav-btn";
        navHtml += '<button type="button" class="' + activeClass + '" onclick="seleccionarVista(' + s.index + ')">' + escapeHtml(s.label) + '</button>';
      }
      var nombre = (usuarioActual && usuarioActual.nombre) ? usuarioActual.nombre : "";
      var rol = (usuarioActual && usuarioActual.rol) ? usuarioActual.rol : "";

      root.innerHTML =
        '<div class="header">' +
          '<div class="header-title">Easy Sale - Punto de Venta</div>' +
          '<div class="header-user">' +
            '<span>Usuario: ' + escapeHtml(nombre) + ' (' + escapeHtml(rol) + ')</span>' +
            '<button type="button" class="btn-logout" onclick="doLogout()">Cerrar Sesión</button>' +
          '</div>' +
        '</div>' +
        '<div class="layout">' +
          '<div class="sidebar">' + navHtml + '</div>' +
          '<div class="main-content"><div id="vista-body" class="box">Cargando...</div></div>' +
        '</div>';
    }

    function seleccionarVista(index) {
      vistaActual = index;
      renderDashboard();
      cargarVista(index);
    }

    function cargarVista(index) {
      var body = document.getElementById("vista-body");
      if (body) {
        body.innerHTML = '<div class="empty-msg">Cargando sección...</div>';
      }
      var xhr = new XMLHttpRequest();
      xhr.open("GET", "/api/vista/" + index, true);
      xhr.onreadystatechange = function () {
        if (xhr.readyState === 4) {
          var currentBody = document.getElementById("vista-body");
          if (!currentBody) return;
          if (xhr.status === 200) {
            var data = JSON.parse(xhr.responseText);
            currentBody.innerHTML = renderSeccion(data.index, data.seccion, data.payload);
          } else {
            currentBody.innerHTML = '<div class="error-msg">Error al cargar la sección (código ' + xhr.status + ').</div>';
          }
        }
      };
      xhr.send();
    }

    if (usuarioActual && usuarioActual.id_usuario) {
      renderDashboard();
      cargarVista(0);
    } else {
      renderLogin("");
    }
  </script>
</body>
</html>"""

    return render_template_string(
        html,
        usuario_json=usuario_json,
        secciones=secciones,
    )


@app.route("/")
def index():
    usuario_actual = session.get("usuario_actual")
    return _render_app_shell(usuario_actual)


@app.route("/api/login", methods=["POST"])
def api_login():
    data = request.get_json(silent=True) or {}
    login_view = LoginView(db)
    res = login_view.intentar_login(data.get("usuario"), data.get("password"))
    if res.get("ok"):
        session["usuario_actual"] = res.get("usuario")
    return jsonify(res)


@app.route("/api/logout", methods=["POST"])
def api_logout():
    session.pop("usuario_actual", None)
    return jsonify({"ok": True})


@app.route("/api/vista/<int:index>", methods=["GET"])
def api_vista(index):
    usuario_actual = session.get("usuario_actual")
    if not usuario_actual:
        return jsonify({"ok": False, "error": "Sesión no iniciada"}), 401

    vista = _crear_vista(index, usuario_actual)
    nombres = {
        0: "Inicio",
        1: "Ventas",
        2: "Inventario",
        3: "Historial",
        4: "Reportes",
        5: "Usuarios",
        6: "Caja",
        7: "Clientes",
        8: "Configuración",
    }

    if index == 0 and hasattr(vista, "cargar_datos_inicio"):
        payload = vista.cargar_datos_inicio()
    elif index == 2 and hasattr(vista, "cargar_productos"):
        payload = {"productos": vista.cargar_productos(), "formulario": vista.obtener_estado_formulario()}
    elif index == 3 and hasattr(vista, "mostrar_historial"):
        payload = {"ventas": vista.mostrar_historial()}
    elif index == 6 and hasattr(vista, "verificar_estado_caja"):
        payload = vista.verificar_estado_caja()
    elif index == 8 and hasattr(vista, "cargar_configuracion"):
        payload = vista.cargar_configuracion()
    else:
        payload = {"estado": "cargada"}

    return jsonify({
        "ok": True,
        "index": index,
        "seccion": nombres.get(index, "Inicio"),
        "payload": payload,
    })


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
