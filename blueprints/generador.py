from pydoc import splitdoc
from flask import Blueprint, render_template, abort, request, session, Markup
from jinja2 import TemplateNotFound
from .gen_java_plsql import generar_call_plsql, generar_seteo_parametros, generar_java_plsql_constantes, gen_pl_cursor_out

generador_page = Blueprint('generador_page', __name__,
                           template_folder='templates')

tp_campo_formulario_v = '''
<div className="mb-3">
    <label htmlFor="{id}" className="form-label">{label}</label>
    <input type="{tipo}" className="form-control" id="{id}" name="{id}" aria-describedby="{id}Help" value=[[[valoresFormulario.{id}]]] onChange=[[[gestionarCambioValor]]] />
    <div id="{id}Help" className="form-text"></div>
</div>
'''

tp_campo_formulario_h = '''
<div className="row mb-3">
    <label className="col-sm-2 col-form-label" htmlFor="{id}">{label}</label>
    <div className="col-sm-10">
        <input type="{tipo}" className="form-control" id="{id}" name="{id}" aria-describedby="{id}Help" value=[[[valoresFormulario.{id}]]] onChange=[[[gestionarCambioValor]]] />
        <div id="{id}Help" className="form-text"></div>
    </div>
</div>
'''

tp_tabla = '''<table className="table table-hover">
  <thead>
    <tr>
     {cabecera}
    </tr>
  </thead>
  <tbody>
    <tr>
      {datos}
    </tr>
    <tr>
      {datos}
    </tr>
  </tbody>
</table>'''

tp_react_formulario_manejadores = '''function gestionarEnvioFormulario(evt) {
    evt.preventDefault();
    // Aquí puedes usar values para enviar la información
    console.log(valoresFormulario);
}
function gestionarCambioValor(evt) {
    /*
      evt.target es el elemento que ejecuto el evento
      name identifica el input y value describe el valor actual
    */
    const { target } = evt;
    const { name, value } = target;
    /*
      Este snippet:
      1. Clona el estado actual
      2. Reemplaza solo el valor del
         input que ejecutó el evento
    */
    const newValoresFormulario = { ...valoresFormulario, [name]: value };
    // Sincroniza el estado de nuevo
    setValoresFormulario(newValoresFormulario);
    console.log(newValoresFormulario);
}'''


tp_react_componente = '''
/* {nombre_archivo}.page.js */
import [[[useState]]] from "react";
function {nombre_archivo}() [[[
    return (
        <h1>{componente}</h1>
        );
]]]
export default {nombre_archivo};

'''


@generador_page.route('/generar/javaplsql/cursor', methods=['POST', 'GET'])
def java_plsql_cursor():
    parametros_plsql_cursor = ''
    codigo_final_generado = ''

    if request.method == 'POST':
        parametros_plsql_cursor = request.form['parametros_plsql_cursor']

        session['parametros_plsql_cursor'] = parametros_plsql_cursor
        lineas = parametros_plsql_cursor.splitlines()

        codigo_final_generado += gen_pl_cursor_out(lineas)

    else:
        if 'parametros_plsql_cursor' in session:
            parametros_plsql_cursor = session['parametros_plsql_cursor']
    return render_template('generar-java-plsql-cursor.html',
                           parametros_plsql_cursor=parametros_plsql_cursor,
                           codigo_final_generado=codigo_final_generado)


@generador_page.route('/generar/javaplsql', methods=['POST', 'GET'])
def java_plsql():
    parametros_plsql = ''
    codigo_final_generado = ''

    if request.method == 'POST':
        nombre_clase_componente = request.form['nombre_clase_componente']
        nombre_plsql = request.form['nombre_plsql']
        parametros_plsql = request.form['parametros_plsql']
        session['parametros_plsql'] = parametros_plsql
        lineas = parametros_plsql.splitlines()
        codigo_final_generado += generar_java_plsql_constantes(lineas)

        codigo_final_generado += generar_call_plsql(
            nombre_plsql) + '\n'

        codigo_final_generado += generar_seteo_parametros(lineas)

    else:
        if 'parametros_plsql' in session:
            parametros_plsql = session['parametros_plsql']
    return render_template('generar-java-plsql.html',
                           parametros_plsql=parametros_plsql,
                           codigo_final_generado=codigo_final_generado)


def desamblar_campo(linea):
    linea = linea.replace('  ', ' ')
    array = linea.split(';')
    identificador = str(array[0]).lower().replace(' ', '_')
    etiqueta = str(array[0]).capitalize()
    archivo = str(array[0]).title()

    tipo = array[1] if len(array) > 1 else 'text'

    return identificador, tipo, etiqueta, archivo


@generador_page.route('/generar/componente', methods=['POST', 'GET'])
def componente():
    lista_componentes = '''Usuario Registro
Usuario Actualizacion
Usuario Asociar Rol'''
    componentes_generados = []
    try:
        if request.method == 'POST':
            lista_componentes = request.form['lista_componentes']
            session['lista_componentes'] = lista_componentes
            lineas = lista_componentes.splitlines()
            for item in lineas:
                ide, tipo, label, filename = desamblar_campo(item)
                print()
                archivo = filename.replace(' ', '')
                componente_definicion = tp_react_componente.format(
                    componente=label, nombre_archivo=archivo)
                componente_definicion = reemplazar_llave_react(
                    componente_definicion)
                componentes_generados.append(componente_definicion)

        else:
            if 'lista_componentes' in session:
                lista_componentes = session['lista_componentes']

        return render_template('generar-componente.html', componentes_generados=componentes_generados,
                               lista_componentes=lista_componentes)
    except TemplateNotFound:
        abort(404)


@generador_page.route('/generar/tablas', methods=['POST', 'GET'])
def tablas():
    text_area_data = 'ingresar csv'
    codigo_generado = ''
    html_generado = ''
    try:
        if request.method == 'POST':

            text_area_data = request.form['text_area_data']
            session['text_area_data'] = text_area_data
            print(text_area_data)

            lineas = text_area_data.splitlines()
            tabla_cabecera = ''
            tabla_td = ''
            for item in lineas:
                ide, tipo, label, nombre = desamblar_campo(item)

                tabla_cabecera += '<th scope="col">{}</th>'.format(label)
                tabla_td += '<td>{}</td>'.format('item')

            codigo_generado = tp_tabla.format(
                cabecera=tabla_cabecera, datos=tabla_td)

            html_generado = generar_codigo_markup(codigo_generado)

        else:
            if 'text_area_data' in session:
                text_area_data = session['text_area_data']

        return render_template('generar-tabla.html', codigo_generado=codigo_generado,
                               text_area_data=text_area_data, html_generado=html_generado)
    except TemplateNotFound:
        abort(404)


@generador_page.route('/generar/formulario', methods=['POST', 'GET'])
def formularios():
    text_area_data = 'ingresar csv'
    codigo_generado = ''
    tipo_form = 'V'
    arreglo_id_campos = []
    try:
        if request.method == 'POST':

            text_area_data = request.form['text_area_data']
            tipo_form = request.form['tipo_form']
            session['text_area_data'] = text_area_data
            print(text_area_data)

            lineas = text_area_data.splitlines()
            codigo_generado = []
            arreglo_id_campos = []
            for item in lineas:
                ide, tipo, label, nombre = desamblar_campo(item)
                codigo_generado.append(generar_html_input(
                    ide, tipo, label, tipo_form))
                arreglo_id_campos.append('''{id}: "",'''.format(id=ide))

        else:
            if 'text_area_data' in session:
                text_area_data = session['text_area_data']

        codigo_generado = generar_formulario_html(codigo_generado)
        html_generado = generar_codigo_markup(codigo_generado)
        react_generado = generar_react_data_formulario(arreglo_id_campos)

        return render_template('generar-formulario.html', codigo_generado=codigo_generado, tipo_form=tipo_form,
                               text_area_data=text_area_data,
                               html_generado=html_generado,
                               react_generado=react_generado,
                               react_manejadores=tp_react_formulario_manejadores)
    except TemplateNotFound:
        abort(404)


def generar_html_input(ide, tipo, label, tipo_form):
    html_input = ''
    if tipo_form == 'V':
        html_input = tp_campo_formulario_v.format(
            id=ide, tipo=tipo, label=label)
    else:
        html_input = tp_campo_formulario_h.format(
            id=ide, tipo=tipo, label=label)
    html_input = reemplazar_llave_react(html_input)
    return html_input


def generar_formulario_html(arreglo_codigos):
    html = '<form onSubmit={gestionarEnvioFormulario}>'
    for item in arreglo_codigos:
        html += item
    html += '''<button className="btn btn-info">Enviar Formulario</button>
</form>'''
    return html


def generar_codigo_markup(codigo_generado):
    codigo_generado = codigo_generado.replace('className=', 'class=')
    html_generado = Markup(codigo_generado)
    return html_generado


def reemplazar_llave_react(codigo_con_llaves):
    codigo_con_llaves = codigo_con_llaves.replace('[[[', '{')
    codigo_con_llaves = codigo_con_llaves.replace(']]]', '}')
    return codigo_con_llaves


def generar_react_data_formulario(arreglo_codigos):
    react = "const [valoresFormulario, setValoresFormulario] = useState({"
    for item in arreglo_codigos:
        react += item
    react += "});"
    return react


@generador_page.route('/generar/grilla', methods=['POST', 'GET'])
def grilla():
    codigo_sin_formato = ''
    html_generado = ''
    grilla_alto = 3
    grilla_ancho = 2
    try:
        if request.method == 'POST':

            grilla_alto = int(request.form['grilla_alto'])
            grilla_ancho = int(request.form['grilla_ancho'])
            session['grilla_alto'] = grilla_alto
            session['grilla_ancho'] = grilla_ancho
            print(grilla_alto)
            for row in range(grilla_alto):
                codigo_sin_formato += """<div className="row">"""
                for col in range(grilla_ancho):
                    codigo_sin_formato += """<div className="col-auto"> {}-{} </div>""".format(
                        row, col)

                codigo_sin_formato += """</div>"""

                html_generado = codigo_sin_formato.replace(
                    'className=', 'class=')
                html_generado = generar_codigo_markup(html_generado)

        else:
            pass

        return render_template('generar-grilla.html', grilla_alto=grilla_alto,
                               grilla_ancho=grilla_ancho,
                               codigo_sin_formato=codigo_sin_formato,
                               html_generado=html_generado)
    except TemplateNotFound:
        abort(404)
