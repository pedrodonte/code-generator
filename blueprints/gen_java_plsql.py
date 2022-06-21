def generar_call_plsql(plsq_call):

    linea = 'private static final String CALL_SP = "[[[{}]]]"; '.format(
        plsq_call)

    return reemplazar_llave_react(linea)


def gen_pl_cursor_out(lineas):
    output_code = '''
ResultSet resultSet = (ResultSet) callableStatement.getObject(POSICION_PARAMETRO_CURSOR);
List<ItemRegistroCursor> listadoItemsCursor = new ArrayList<ItemRegistroCursor>();
while (resultSet.next()) {
    ItemRegistroCursor item = new ItemRegistroCursor();
'''
    nro_parametro = 1

    for item in lineas:
        nombre, clase = desamblar_pojo_setter(
            item, nro_parametro)
        nombre = get_nombre_setter(nombre)
        type_setter = get_type_setter(clase)
        output_code += '    item.set{}(resultSet.get{}({}));'.format(
            nombre, type_setter, nro_parametro) + '\n'
        nro_parametro += 1
    output_code += '''
    listadoItemsCursor.add(item);
}'''
    return output_code


def get_nombre_setter(nombre):
    return nombre[0].upper()+nombre[1:]


def get_type_setter(nombre):
    return nombre[0].upper()+nombre[1:]


def desamblar_pojo_setter(linea, nro):

    linea = linea.replace('  ', ' ')
    array = linea.split(' ')
    if len(array) < 2:
        raise AssertionError('Revisar parametros del PLSQL, falta algun valor')
    # paciente.setSexo(cursorPaciente.getString(4));

    nombre = str(array[2])[:-1]
    clase = str(array[1]).capitalize().replace(' ', '')
    print(nombre, clase)
    return nombre, clase


def generar_seteo_parametros(lineas):
    output_code = ''
    nro_parametro = 1
    for item in lineas:
        constante, atributo_java, tipo, io, oracle_type = desamblar_parametro_plsql(
            item, nro_parametro)

        atributo_java = atributo_java.lower()
        if io == 'IN':
            output_code += 'callableStatement.set{}({}, {});'.format(
                tipo, constante, atributo_java) + '\n'
        else:

            output_code += 'callableStatement.registerOutParameter({}, {});'.format(
                constante, oracle_type) + '\n'
        nro_parametro += 1

    output_code += 'callableStatement.executeUpdate();'

    return output_code


def reemplazar_llave_react(codigo_con_llaves):
    codigo_con_llaves = codigo_con_llaves.replace('[[[', '{')
    codigo_con_llaves = codigo_con_llaves.replace(']]]', '}')
    return codigo_con_llaves


def desamblar_parametro_plsql(linea, nro_parametro):
    linea = linea.replace('  ', ' ')
    array = linea.split(';')
    if len(array) < 2:
        raise Exception('Revisar parametros del PLSQL, falta algun valor')
    # Nombre_Parametro;I/O;Tipo

    io = str(array[1]).upper()
    tipo = str(array[2]).upper()
    atributo_java = str(array[0]).capitalize().replace(' ', '')

    constante = str(array[0]).upper().replace(' ', '_')
    oracle_type = ''
    if tipo.find('VARCHAR') == 0:
        tipo = 'String'
        oracle_type = 'Types.VARCHAR'
    elif tipo.find('CURSOR') == 0:
        tipo = 'CURSOR'
        oracle_type = 'OracleTypes.CURSOR'
    elif tipo.find('NUMERIC') == 0:
        tipo = 'Int'
        oracle_type = 'Types.INTEGER'
    else:
        tipo = 'DESCONOCIDO'
        oracle_type = 'DESCONOCIDO'

    constante = '{}_{}_{}'.format(
        io, nro_parametro, constante)

    return constante, atributo_java, tipo, io, oracle_type


def generar_java_plsql_constantes(lineas):
    output_code = ''
    nro_parametro = 1
    for item in lineas:
        constante, atributo_java, tipo, io, oracle_type = desamblar_parametro_plsql(
            item, nro_parametro)

        constante = 'private static final int {} = {};'.format(
            constante, nro_parametro)

        nro_parametro += 1
        output_code += constante + '\n'
    return output_code
