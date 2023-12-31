import pyparsing as pyp

class Query:
    def __init__(cls,query) -> None:
        cls.query = query
        cls.bin_op = pyp.one_of([">", "<", ">=", "<=", "=", "<>"]).set_name("comparator")
        cls.LPAREN, cls.RPAREN, cls.EQUAL, cls.stmtTerm = map(pyp.Suppress, "()=;")
        cls.SELECT, cls.CREATE, cls.DROP, cls.SHOW, cls.INSERT, cls.DELETE = cls.command_mapping("SELECT, CREATE, DROP, SHOW, INSERT, DELETE")
        cls.UPDATE, cls.NOT, cls.UNIQUE, cls.PRIMARY, cls.KEY, cls.TABLES = cls.command_mapping("UPDATE, NOT, UNIQUE, PRIMARY, KEY, TABLES")
        cls.TABLE, cls.INDEX, cls.VALUES, cls.FROM, cls.INTO, cls.WHERE, cls.SET = cls.command_mapping("TABLE, INDEX, VALUES, FROM, INTO, WHERE, SET")
        cls.NULL, cls.TINYINT, cls.SMALLINT, cls.INT, cls.BIGINT, cls.LONG = cls.command_mapping("NULL, TINYINT, SMALLINT, INT, BIGINT, LONG")
        cls.FLOAT, cls.DOUBLE, cls.YEAR, cls.TIME, cls.DATETIME, cls.DATE, cls.TEXT = cls.command_mapping("FLOAT, DOUBLE, YEAR, TIME, DATETIME, DATE, TEXT")
        cls.data_type = (cls.NULL | cls.TINYINT | cls.SMALLINT | cls.INT | cls.BIGINT |cls.LONG | cls.FLOAT | cls.DOUBLE | cls.YEAR
             | cls.TIME | cls.DATETIME | cls.DATE | cls.TEXT)
        cls.data_type.set_name("data type")
        cls.keyword = (cls.SELECT | cls.CREATE | cls.DROP | cls.SHOW | cls.INSERT | cls.DELETE | cls.UPDATE | cls.NOT | cls.UNIQUE | cls.PRIMARY 
            | cls.KEY | cls.TABLES | cls.TABLE | cls.INDEX | cls.VALUES | cls.FROM | cls.INTO | cls.WHERE | cls.SET | cls.data_type)
        cls.keyword.set_name("keyword")
        cls.db_tables, cls.db_columns = map(pyp.CaselessLiteral, ("davisbase_tables", "davisbase_columns"))
        cls.reserved_identifiers = cls.db_tables | cls.db_columns
        cls.reserved_identifiers.set_name("reserved identfier")
        cls.identifier =  ~cls.keyword + pyp.Word(pyp.alphas, pyp.alphanums + "_")
        cls.identifier.set_name("identifier")
        cls.show_table_stmt = cls.SHOW + cls.TABLES + cls.stmtTerm
        cls.NOT_NULL = pyp.Group(cls.NOT + cls.NULL).set_parse_action(lambda: "NOT_NULL")
        cls.PRIMARY_KEY = pyp.Group(cls.PRIMARY + cls.KEY).set_parse_action(lambda: "PRIMARY_KEY")
        cls.column_contstraint_opts = cls.UNIQUE | cls.PRIMARY_KEY | cls.NOT_NULL
        cls.column_contstraints = cls.column_contstraint_opts * (0, 3)
        cls.column_contstraints.set_parse_action(cls.constraint_semantics)
        cls.new_col_name = ~cls.reserved_identifiers + cls.identifier
        cls.column_definition = cls.new_col_name + cls.data_type + cls.column_contstraints
        cls.column_definition.set_parse_action(cls.column_definition_semantics)
        cls.multi_column_definitions = cls.LPAREN + pyp.delimited_list(cls.column_definition) + cls.RPAREN
        cls.new_table_name = cls.new_col_name.copy()

        cls.integer = pyp.Regex(r"[+-]?\d+")
        cls.integer.set_name("int")

        cls.numeric_literal = pyp.Regex(r"[+-]?\d*\.?\d+([eE][+-]?\d+)?")
        cls.numeric_literal.set_name("real number")

        cls.string_literal = pyp.quoted_string.set_parse_action(lambda toks: str.replace(toks[0], "'", "").replace('"', ""))
        cls.string_literal.set_name("string")

        cls.literal_value = (
            cls.numeric_literal
            | cls.string_literal
            | cls.NULL
        )

        cls.literal_value.set_name("value literal")
        cls.value_list = pyp.Suppress(cls.VALUES) + cls.LPAREN + pyp.delimited_list(cls.literal_value) + cls.RPAREN
        cls.value_list.set_name("list of column values")

        cls.column_list = cls.LPAREN + pyp.delimited_list(cls.identifier) + cls.RPAREN
        cls.column_list.set_name("paranthesized column name list")

        cls.predicate = (pyp.Opt(cls.NOT).set_parse_action(lambda x: "TRUE" if x else "FALSE")
             + cls.identifier 
             + cls.bin_op 
             + cls.literal_value)
        cls.predicate.set_parse_action(lambda list1: {
            "negated": list1[0],
            "column_name": list1[1],
            "comparator": list1[2],
            "value": list1[3]
        })     
        
        cls.where_clause = pyp.Suppress(cls.WHERE) + cls.predicate

        cls.set_clause = pyp.Suppress(cls.SET) + cls.identifier + cls.EQUAL + cls.literal_value

        cls.set_clause.set_parse_action(lambda list1: {
            "column_name": list1[0],
            "comparator": "=",
            "value": list1[1]
        })

        cls.select_clause = (cls.SELECT 
                + pyp.Group(pyp.Literal("*") | pyp.delimited_list(cls.identifier))
                )

        cls.create_table_stmt = (pyp.Group(cls.CREATE + cls.TABLE).set_parse_action(lambda ls: " ".join(ls[0]))
            + cls.new_table_name 
            + cls.multi_column_definitions 
            + cls.stmtTerm
        )

        cls.create_table_stmt.set_parse_action(cls.table_creation_semantics)

        cls.drop_table_stmt = (pyp.Group(cls.DROP + cls.TABLE).set_parse_action(lambda ls: " ".join(ls[0]))
            + cls.identifier
            + cls.stmtTerm
        )

        cls.drop_table_stmt.set_parse_action(lambda list1: {
            "command": list1[0],
            "table_name": list1[1],
        })

        cls.create_index_stmt = (pyp.Group(cls.CREATE + cls.INDEX).set_parse_action(lambda ls: " ".join(ls[0]))
            + cls.identifier
            + cls.LPAREN + cls.identifier + cls.RPAREN
            + cls.stmtTerm
        )
        cls.create_index_stmt.set_parse_action(lambda list1: {
            "command": list1[0],
            "table_name": list1[1],
            "column_name": list1[2]
        })

        cls.drop_index_stmt = (pyp.Group(cls.DROP + cls.INDEX).set_parse_action(lambda ls: " ".join(ls[0]))
            + cls.identifier
            + cls.LPAREN + cls.identifier + cls.RPAREN
            + cls.stmtTerm
        )
        cls.drop_index_stmt.set_parse_action(lambda list1: {
            "command": list1[0],
            "table_name": list1[1],
            "column_name": list1[2]
        })
        cls.insert_row_stmt = (pyp.Group(cls.INSERT + cls.INTO + cls.TABLE).set_parse_action(lambda ls: " ".join(ls[0]))
            + pyp.Opt(cls.column_list).set_parse_action(lambda x: [x])
            + cls.identifier
            + cls.value_list.set_parse_action(lambda x: [x])
            + cls.stmtTerm)
        
        cls.insert_row_stmt.set_parse_action(lambda list1: {
            "command": list1[0],
            "column_name_list": list1[1].as_list(),
            "table_name": list1[2],
            "value_list": list1[3].as_list()
        })

        cls.delete_record_stmt = (cls.DELETE + pyp.Suppress(cls.FROM + cls.TABLE) 
                     + cls.identifier +pyp. Opt(cls.where_clause).set_parse_action(lambda list1: list1 or {}) 
                     + cls.stmtTerm)

        
        cls.delete_record_stmt.set_parse_action(lambda list1: {
            "command": list1[0],
            "table_name": list1[1],
            "condition": list1[2]
        })
        
        cls.update_record_stmt = (
            cls.UPDATE 
            + cls.identifier 
            + cls.set_clause
            + pyp.Opt(cls.where_clause).set_parse_action(lambda list1: list1 or {})
            + cls.stmtTerm
        )

        cls.update_record_stmt.set_parse_action(lambda list1: {
            "command": list1[0],
            "table_name": list1[1],
            "operation": list1[2],
            "condition": list1[3]
        })

        cls.select_statement = (cls.select_clause 
            + pyp.Suppress(cls.FROM)
            + cls.identifier
            + pyp.Opt(cls.where_clause).set_parse_action(lambda list1: list1 or {})
            + cls.stmtTerm)

        cls.select_statement.set_parse_action(lambda list1: {
            "command": list1[0],
            "column_name_list": [] if "*" in (x := list1[1].as_list()) else x,
            "table_name": list1[2],
            "condition": list1[3]
        })

        cls.show_table_stmt.set_parse_action(
            lambda: cls.select_statement.parse_string("SELECT table_name FROM system_tables;")
        )

        cls.NULL.set_parse_action(lambda: "")

        cls.statement = (cls.create_table_stmt | cls.drop_table_stmt | cls.drop_index_stmt | cls.create_index_stmt | cls.insert_row_stmt
             | cls.delete_record_stmt | cls.update_record_stmt | cls.select_statement | cls.show_table_stmt)


    @classmethod
    def constraint_semantics(cls,constraint_list):
        constraint_set = set(constraint_list)
        constraint_dict = {
            "column_key": "",
            "is_nullable": "YES"
        }
        if "PRIMARY_KEY" in constraint_set:
            constraint_dict["column_key"] = "PRI"
            constraint_dict["is_nullable"] = "NO"
        elif "UNIQUE" in constraint_set:
            constraint_dict["column_key"] = "UNI"
            constraint_dict["is_nullable"] = "NO"
        if "NOT_NULL" in constraint_set:
            constraint_dict["is_nullable"] = "NO"
        return constraint_dict
    
    @classmethod
    def command_mapping(cls,string):
        lst = map(str.strip, string.split(","))
        return map(pyp.CaselessKeyword, lst)
    
    @classmethod
    def column_definition_semantics(cls,def_list):
        name, d_type, prop_dict = def_list
        prop_dict["column_name"] = name
        prop_dict["data_type"] = d_type
        return prop_dict
    
    @classmethod
    def table_creation_semantics(cls,parse_list):
        cmd, t_name, = parse_list[0:2]
        col_json_list = parse_list[2:]    
        columns_list = []
        for i, col_json in enumerate(col_json_list):
            col_json["column_position"] = i+1
            col_json["table_name"] = t_name
            columns_list.append(col_json)
        return {
            "command": cmd,
            "table_name": t_name,
            "column_list": columns_list
        } 

    def parse(cls):
        return cls.statement.parse_string(cls.query)

