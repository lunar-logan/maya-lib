import sys
import lexer
import ply.yacc as yacc

# The token map
tokens = lexer.tokens

# My local symbol table
symTabl = {}

########################
# # For debugging purpose
DEBUG = False
#########################

precedence = (
('left', 'PLUS', 'MINUS'),
('left', 'TIMES', 'DIVIDE'),
)
# Grammar description
start = 'goal_symbol'

def p_goal_symbol(p):
    '''goal_symbol : compilation'''
    p[0] = ('goal-symbol', p[1])

def p_pragma(p):
    '''pragma  : PRAGMA IDENTIFIER SEMICOLON
    | PRAGMA simple_name LPAREN pragma_arg_s RPAREN SEMICOLON'''
    pass
def p_pragma_arg_s(p):
    '''pragma_arg_s : pragma_arg
    | pragma_arg_s COMMA pragma_arg'''
    pass
def p_pragma_arg(p):
    '''pragma_arg : expression
    | simple_name ARROW expression'''
    pass
def p_pragma_s(p):
    '''pragma_s :
    | pragma_s pragma'''
    if len(p) == 3:
        p[0] = ('pragma', p[2])
    else:
        p[0] = None
def p_decl(p):
    '''decl    : object_decl
    | number_decl
    | type_decl
    | subtype_decl
    | subprog_decl
    | pkg_decl
    | task_decl
    | prot_decl
    | exception_decl
    | rename_decl
    | generic_decl
    | body_stub
    | error SEMICOLON'''
    p[0] = p[1]
    
def p_object_decl(p):
    '''object_decl : def_id_s COLON object_qualifier_opt object_subtype_def init_opt SEMICOLON'''
    ##p[0] = ('object-decl', p[1], p[3], p[4], p[5])
    if p[3] is not None:
        if p[5] is not None:
            p[0] = ('object-decl', p[1], p[3], p[4], p[5])
        else:
            p[0] = ('object-decl', p[1], p[3], p[4])
    elif p[5] is not None:
        p[0] = ('object-decl', p[1], p[4], p[5])
    else:
        p[0] = ('object-decl', p[1], p[4])

def p_def_id_s(p):
    '''def_id_s : def_id
    | def_id_s COMMA def_id'''
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = p[1] + p[3]

def p_def_id(p):
    '''def_id  : IDENTIFIER'''
    p[0] = ('def-id', p[1])
    
def p_object_qualifier_opt(p):
    '''object_qualifier_opt :
    | ALIASED
    | CONSTANT
    | ALIASED CONSTANT'''
    if len(p) == 3:
        p[0] = ('object-qualified-opt', p[1], p[2])
    elif len(p) == 2:
        p[0] = ('object-qualified-opt', p[1])
    else:
        p[0] = None
def p_object_subtype_def(p):
    '''object_subtype_def : subtype_ind
    | array_type'''
    p[0] = ('object-subtype-def', p[1])
def p_init_opt(p):
    '''init_opt :
    | IS_ASSIGNED expression'''
    if len(p) == 3:
        p[0] = ('init-opt', p[2])
def p_number_decl(p):
    '''number_decl : def_id_s COLON CONSTANT IS_ASSIGNED expression SEMICOLON'''
    p[0] = ('number-decl', p[1], p[5])

def p_type_decl(p):
    '''type_decl : TYPE IDENTIFIER discrim_part_opt type_completion SEMICOLON'''
    ##p[0] = ('type-decl', p[2], p[3], p[4])
    if p[3] is not None:
        p[0] = ('type-decl', p[2], p[3], p[4])
    else: p[0] = ('type-decl', p[2], p[4])
    
def p_discrim_part_opt(p):
    '''discrim_part_opt :
    | discrim_part
    | LPAREN BOX RPAREN'''
    if len(p) == 3:
        p[0] = ('discrim-part-opt', p[2])
    elif len(p) == 2:
        p[0] = ('discrim-part-opt', p[1])
    else:
        p[0] = None
def p_type_completion(p):
    '''type_completion :
    | IS type_def'''
    if len(p) == 3:
        p[0] = ('type-completion', p[2])
    else:
        p[0] = None
        
def p_type_def(p):
    '''type_def : enumeration_type 
    | integer_type
    | real_type
    | array_type
    | record_type
    | access_type
    | derived_type
    | private_type'''
    p[0] = p[1]
    
def p_subtype_decl(p):
    '''subtype_decl : SUBTYPE IDENTIFIER IS subtype_ind SEMICOLON'''
    p[0] = ('subtype-decl', p[2], p[4])
def p_subtype_ind(p):
    '''subtype_ind : name constraint
    | name'''
    if len(p) == 3:
        p[0] = ('subtype-ind', p[1], p[2])
    else:
        p[0] = ('subtype-ind', p[1])
        
def p_constraint(p):
    '''constraint : range_constraint
    | decimal_digits_constraint'''
    p[0] = ('constraint', p[1])
    
def p_decimal_digits_constraint(p):
    '''decimal_digits_constraint : DIGITS expression range_constr_opt'''
    ##p[0] = ('decimal-digits-constraint', p[2], p[3])
    if p[3] is not None:
        p[0] = ('decimal-digits-constraint', p[2], p[3])
    else:
        p[0] = ('decimal-digits-constraint', p[2])
        
def p_derived_type(p):
    '''derived_type : NEW subtype_ind
    | NEW subtype_ind WITH PRIVATE
    | NEW subtype_ind WITH record_def
    | ABSTRACT NEW subtype_ind WITH PRIVATE
    | ABSTRACT NEW subtype_ind WITH record_def'''
    pass
def p_range_constraint(p):
    '''range_constraint : RANGE range'''
    p[0] = ('range-constraint', p[2])
    
def p_range(p):
    '''range : simple_expression DOUBLEDOT simple_expression
    | name TICK RANGE
    | name TICK RANGE LPAREN expression RPAREN'''
    n = len(p)
    if n == 4 and p[2] == '..':
        p[0] = ('range', p[1], p[3])
    elif n == 4 and p[2] == lexer.t_TICK:
        p[0] = ('range', p[1])
    else:
        p[0] = ('range', p[1], p[5])

def p_enumeration_type(p):
    '''enumeration_type : LPAREN enum_id_s RPAREN'''
    p[0] = ('enumeration', p[2])

def p_enum_id_s(p):
    '''enum_id_s : enum_id
    | enum_id_s COMMA enum_id'''
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = p[1] + p[3]

def p_enum_id(p):
    '''enum_id : IDENTIFIER
    | CHARACTER'''
    p[0] = ('enum-id', p[1])
    
def p_integer_type(p):
    '''integer_type : range_spec
    | MOD expression'''
    if len(p) == 2:
        p[0] = ('integer-type', p[1])
    else:
        p[0] = ('integer-type', p[2])

def p_range_spec(p):
    '''range_spec : range_constraint'''
    p[0] = ('range-spec', p[1])
    
def p_range_spec_opt(p):
    '''range_spec_opt :
    | range_spec'''
    if len(p) == 2:
        p[0]= ('range-spec-opt', p[1])
    else:
        p[0] = None
        
def p_real_type(p):
    '''real_type : float_type
    | fixed_type'''
    p[0] = ('real-type', p[1])
    
def p_float_type(p):
    '''float_type : DIGITS expression range_spec_opt'''
    #p[0] = ('float-type', p[2], p[3])
    if p[3] is not None:
        p[0] = ('float-type', p[2], p[3])
    else:
        p[0] = ('float-type', p[2])
def p_fixed_type(p):
    '''fixed_type : DELTA expression range_spec
    | DELTA expression DIGITS expression range_spec_opt'''
    if len(p) == 4:
        p[0]= ('fixed-type', p[2], p[3])
    else:
        ##p[0] = ('fixed-type', p[2], p[4], p[5])
        if p[5] is not None:
            p[0] = ('fixed-type', p[2], p[4], p[5])
        else:
            p[0] = ('fixed-type', p[2], p[4])
def p_array_type(p):
    '''array_type : unconstr_array_type
    | constr_array_type'''
    p[0] = ('array-type', p[1])
    
def p_unconstr_array_type(p):
    '''unconstr_array_type : ARRAY LPAREN index_s RPAREN OF component_subtype_def'''
    p[0] = ('unconstr-array-type', p[3], p[6])

def p_constr_array_type(p):
    '''constr_array_type : ARRAY iter_index_constraint OF component_subtype_def'''
    p[0] = ('constr-array-type', p[2], p[4])
    
def p_component_subtype_def(p):
    '''component_subtype_def : aliased_opt subtype_ind'''
   ### p[0] = ('component_subtype_def', p[1], p[2])
    if p[1] is not None:
        p[0] = ('component_subtype_def', p[1], p[2])
    else:
        p[0] = ('component_subtype_def', p[2])
def p_aliased_opt(p):
    '''aliased_opt : 
    | ALIASED'''
    if len(p) == 2:
        p[0] = ('aliased-opt', p[1])
    else:
        p[0] = None
def p_index_s(p):
    '''index_s : index
    | index_s COMMA index'''
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = p[1] + p[3]
def p_index(p):
    '''index : name RANGE BOX'''
    p[0] = ('index', p[1])
    
def p_iter_index_constraint(p):
    '''iter_index_constraint : LPAREN iter_discrete_range_s RPAREN'''
    p[0] = ('iter_index_constraint', p[2])
def p_iter_discrete_range_s(p):
    '''iter_discrete_range_s : discrete_range
    | iter_discrete_range_s COMMA discrete_range'''
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = p[1] + p[3]
    
def p_discrete_range(p):
    '''discrete_range : name range_constr_opt
    | range'''
    if len(p) == 3:
        if p[2] is not None:
            p[0] = ('discrete-range', p[1], p[2])
        else:
            p[0] = ('discrete-range', p[1])
    else:
        p[0] = ('discrete-range', p[1])
    
def p_range_constr_opt(p):
    '''range_constr_opt :
    | range_constraint'''
    if len(p) == 2:
        p[0] = ('range-constraint-opt', p[1])
    else:
        p[0] = None

def p_record_type(p):
    '''record_type : tagged_opt limited_opt record_def'''
    pass

def p_record_def(p):
    '''record_def : RECORD pragma_s comp_list END RECORD
    | NULL RECORD'''
    pass
def p_tagged_opt(p):
    '''tagged_opt :
    | TAGGED
    | ABSTRACT TAGGED'''
    pass
def p_comp_list(p):
    '''comp_list : comp_decl_s variant_part_opt
    | variant_part pragma_s
    | NULL SEMICOLON pragma_s'''
    pass
def p_comp_decl_s(p):
    '''comp_decl_s : comp_decl
    | comp_decl_s pragma_s comp_decl'''
    pass
def p_variant_part_opt(p):
    '''variant_part_opt : pragma_s
    | pragma_s variant_part pragma_s'''
    pass
def p_comp_decl(p):
    '''comp_decl : def_id_s COLON component_subtype_def init_opt SEMICOLON
    | error SEMICOLON'''
    pass
def p_discrim_part(p):
    '''discrim_part : LPAREN discrim_spec_s RPAREN'''
    pass
def p_discrim_spec_s(p):
    '''discrim_spec_s : discrim_spec
    | discrim_spec_s SEMICOLON discrim_spec'''
    pass
def p_discrim_spec(p):
    '''discrim_spec : def_id_s COLON access_opt mark init_opt
    | error'''
    pass
def p_access_opt(p):
    '''access_opt :
    | ACCESS'''
    pass
def p_variant_part(p):
    '''variant_part : CASE simple_name IS pragma_s variant_s END CASE SEMICOLON'''
    pass
def p_variant_s(p):
    '''variant_s : variant
    | variant_s variant'''
    pass
def p_variant(p):
    '''variant : WHEN choice_s ARROW pragma_s comp_list'''
    pass
def p_choice_s(p):
    '''choice_s : choice
    | choice_s '|' choice'''
    pass
def p_choice(p):
    '''choice : expression
    | discrete_with_range
    | OTHERS'''
    pass
def p_discrete_with_range(p):
    '''discrete_with_range : name range_constraint
    | range'''
    pass
def p_access_type(p):
    '''access_type : ACCESS subtype_ind
    | ACCESS CONSTANT subtype_ind
    | ACCESS ALL subtype_ind
    | ACCESS prot_opt PROCEDURE formal_part_opt
    | ACCESS prot_opt FUNCTION formal_part_opt RETURN mark'''
    pass
def p_prot_opt(p):
    '''prot_opt :
    | PROTECTED'''
    pass
def p_decl_part(p):
    '''decl_part :
    | decl_item_or_body_s1'''
    if len(p) == 2:
        p[0] = ('decl-part', p[1])
    else:
        p[0] = None
def p_decl_item_s(p):
    '''decl_item_s : 
    | decl_item_s1'''
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = None
                
def p_decl_item_s1(p):
    '''decl_item_s1 : decl_item
    | decl_item_s1 decl_item'''
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = p[1] + p[2]
        
def p_decl_item(p):
    '''decl_item : decl
    | use_clause
    | rep_spec
    | pragma'''
    p[0] = p[1]
    
def p_decl_item_or_body_s1(p):
    '''decl_item_or_body_s1 : decl_item_or_body
    | decl_item_or_body_s1 decl_item_or_body'''
    if len(p) == 2:
        p[0] = p[1]
    else: p[0] = p[1] + p[2]
def p_decl_item_or_body(p):
    '''decl_item_or_body : body
    | decl_item'''
    p[0] = p[1] #('decl_item_or_body', p[1])
def p_body(p):
    '''body : subprog_body
    | pkg_body
    | task_body
    | prot_body'''
    p[0] = ('body', p[1])
def p_name(p):
    '''name : simple_name
    | indexed_comp
    | selected_comp
    | attribute
    | operator_symbol'''
    p[0] = ('name', p[1])
def p_mark(p):
    '''mark : simple_name
    | mark TICK attribute_id
    | mark DOT simple_name'''
    if len(p) == 2:
        p[0] = p[1]
    else:
        if p[2] == "'" :
            p[0] = p[1] + p[3]
        else:
            p[0] = p[1] + p[3]
        
def p_simple_name(p):
    '''simple_name : IDENTIFIER'''
    p[0] = ('simple-name', p[1])
    
def p_compound_name(p):
    '''compound_name : simple_name
    | compound_name DOT simple_name'''
    if len(p) == 2:
        p[0] = ('compound-name', p[1])
    else:
        p[0] = ('compound-name', (p[1], p[3]))
    
def p_c_name_list(p):
    '''c_name_list : compound_name
     | c_name_list COMMA compound_name'''
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = p[1] + p[3]
    
def p_used_char(p):
    '''used_char : CHARACTER'''
    p[0] = ('used-char', p[1])
    
def p_operator_symbol(p):
    '''operator_symbol : STRING'''
    p[0] = ('operator-symbol', p[1])
    
def p_indexed_comp(p):
    '''indexed_comp : name LPAREN value_s RPAREN'''
    p[0] = ('indexed-comp', p[1], p[3])
def p_value_s(p):
    '''value_s : value
    | value_s COMMA value'''
    if len(p) == 2: p[0] = p[1]
    else: p[0] = p[1] + p[3]
    
def p_value(p):
    '''value : expression
    | comp_assoc
    | discrete_with_range
    | error'''
    p[0] = ('value', p[1])
    
def p_selected_comp(p):
    '''selected_comp : name DOT simple_name
    | name DOT used_char
    | name DOT operator_symbol
    | name DOT ALL'''
    p[0] = ('selected-comp', p[1], p[3])
    
def p_attribute(p):
    '''attribute : name TICK attribute_id'''
    p[0] = ('attribute', p[1], p[3])
    
def p_attribute_id(p):
    '''attribute_id : IDENTIFIER
    | DIGITS
    | DELTA
    | ACCESS'''
    p[0] = ('attribute-id', p[1])
    
def p_literal(p):
    '''literal : NUMBER
    | used_char
    | NULL'''
    p[0] = ('literal', p[1])
    
def p_aggregate(p):
    '''aggregate : LPAREN comp_assoc RPAREN
    | LPAREN value_s_2 RPAREN
    | LPAREN expression WITH value_s RPAREN
    | LPAREN expression WITH NULL RECORD RPAREN
    | LPAREN NULL RECORD RPAREN'''
    pass
def p_value_s_2(p):
    '''value_s_2 : value COMMA value
    | value_s_2 COMMA value'''
    p[0] = p[1] + p[3]
def p_comp_assoc(p):
    '''comp_assoc : choice_s ARROW expression'''
    p[0] = ('comp-assoc', p[1], p[3])
def p_expression(p):
    '''expression : relation
    | expression logical relation
    | expression short_circuit relation'''
    n = len(p)
    if n == 2:
        p[0] = p[1]
    elif n == 4:
        p[0] = p[1] + p[2] + p[3]
    else:
        p[0] = p[1] + p[2] + p[3]
def p_logical(p):
    '''logical : AND
    | OR
    | XOR'''
    p[0] = ('logical', p[1])
    
def p_short_circuit(p):
    '''short_circuit : AND THEN
    | OR ELSE'''
    p[0] = ('short-circuit', p[1], p[2])
    
def p_relation(p):
    '''relation : simple_expression
    | simple_expression relational simple_expression
    | simple_expression membership range
    | simple_expression membership name'''
    if len(p) == 2:
        p[0] = ('relation', p[1])
    else:
        p[0] = ('relation', p[1], p[2], p[3])
        
def p_relational(p):
    '''relational : EQ
    | NE
    | LT
    | LE
    | GT
    | GE'''
    p[0] = ('relational', p[1])
def p_membership(p):
    '''membership : IN
    | NOT IN'''
    if len(p) == 2: p[0] = ('membership', p[1])
    else: p[0] = ('membership', p[1], p[2])
    
def p_simple_expression(p):
    '''simple_expression : unary term
    | term
    | simple_expression adding term'''
    n = len(p)
    if n == 3:
        p[0] = p[1] + p[2]
    elif n == 2: p[0] = p[1]
    else: p[0] = p[1] + p[2] + p[3]
def p_unary(p):
    '''unary   : PLUS
    | MINUS'''
    p[0] = ('unary', p[1])
def p_adding(p):
    '''adding  : PLUS
    | MINUS
    | AMPERSAND'''
    p[0] = ('adding', p[1])
    
def p_term(p):
    '''term    : factor
    | term multiplying factor'''
    if len(p) == 2: p[0] = p[1]
    else: p[0] = p[1] + p[2] + p[3]
    
def p_multiplying(p):
    '''multiplying : TIMES
    | DIVIDE
    | MOD
    | REM'''
    p[0] = ('multiplying', p[1])
def p_factor(p):
    '''factor : primary
    | NOT primary
    | ABS primary
    | primary POW primary'''
    n = len(p)
    if n == 2: p[0] = p[1]
    elif n == 3: p[0] = p[1] + p[2]
    else: p[0] = p[1] + p[2] + p[3]
    
def p_primary(p):
    '''primary : literal
    | name
    | allocator
    | qualified
    | parenthesized_primary'''
    p[0] = ('primary', p[1])
    
def p_parenthesized_primary(p):
    '''parenthesized_primary : aggregate
    | LPAREN expression RPAREN'''
    if len(p) == 2: p[0] = ('parenthesized_primary', p[1])
    else: ('parenthesized_primary', p[2])
    
def p_qualified(p):
    '''qualified : name TICK parenthesized_primary'''
    p[0] = ('qualified', p[1], p[3])
    
def p_allocator(p):
    '''allocator : NEW name
    | NEW qualified'''
    p[0] = ('allocator', p[2])

def p_statement_s(p):
    '''statement_s : statement
    | statement_s statement'''
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = p[1] + p[2]
        
def p_statement(p):
    '''statement : unlabeled
    | label statement'''
    if len(p) == 2:
        p[0] = ('statement', p[1])
    else:
        p[0] = ('statement', p[1], p[2])

def p_unlabeled(p):
    '''unlabeled : simple_stmt
    | compound_stmt
    | pragma'''
    p[0] = ('unlabeled', p[1])

def p_simple_stmt(p):
    '''simple_stmt : NULL_stmt
    | assign_stmt
    | exit_stmt
    | return_stmt
    | goto_stmt
    | procedure_call
    | delay_stmt
    | abort_stmt
    | raise_stmt
    | code_stmt
    | requeue_stmt
    | error SEMICOLON'''
    p[0] = ('simple-stmt', p[1])
def p_compound_stmt(p):
    '''compound_stmt : if_stmt
    | case_stmt
    | loop_stmt
    | block
    | accept_stmt
    | select_stmt'''
    p[0] = ('compound-stmt', p[1])

def p_label(p):
    '''label : LLB IDENTIFIER RLB'''
    p[0] = ('label', p[2])
    
def p_NULL_stmt(p):
    '''NULL_stmt : NULL SEMICOLON'''
    p[0] = ('null-stmt', p[1])
def p_assign_stmt(p):
    '''assign_stmt : name IS_ASSIGNED expression SEMICOLON'''
    p[0] = ('assign-stmt', p[1], p[3])
def p_if_stmt(p):
    '''if_stmt : IF cond_clause_s else_opt END IF SEMICOLON'''
    if p[3] is not None:
        p[0] = ('if-stmt', p[2], p[3])
    else:
        p[0] = ('if-stmt', p[2])
def p_cond_clause_s(p):
    '''cond_clause_s : cond_clause
    | cond_clause_s ELSIF cond_clause'''
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = p[1] + p[3]
        
def p_cond_clause(p):
    '''cond_clause : cond_part statement_s'''
    p[0] = ('cond-clause', p[1], p[2])
def p_cond_part(p):
    '''cond_part : condition THEN'''
    p[0] = ('cond-part', p[1])
    
def p_condition(p):
    '''condition : expression'''
    p[0] = ('condition', p[1])
def p_else_opt(p):
    '''else_opt :
    | ELSE statement_s'''
    if len(p) == 3:
        p[0] = ('else-opt', p[2])
    else:
        p[0] = None
def p_case_stmt(p):
    '''case_stmt : case_hdr pragma_s alternative_s END CASE SEMICOLON'''
    if p[3] is not None:
        p[0] = ('case-stmt', p[1], p[2], p[3])
    else:
        p[0] = ('case-stmt', p[1], p[2])
def p_case_hdr(p):
    '''case_hdr : CASE expression IS'''
    p[0] = ('case-hdr', p[2])
def p_alternative_s(p):
    '''alternative_s :
    | alternative_s alternative'''
    if len(p) == 3:
        p[0] = ('alternative-s', p[1], p[2])
    else:
        p[0] = None
def p_alternative(p):
    '''alternative : WHEN choice_s ARROW statement_s'''
    p[0] = ('alternative', p[2], p[4])
    
def p_loop_stmt(p):
    '''loop_stmt : label_opt iteration basic_loop id_opt SEMICOLON'''
    p[0] = ('loop-stmt', p[1], p[2], p[3], p[4])
    if p[1] is not None:
        if p[4] is not None:
            p[0] = ('loop-stmt', p[1], p[2], p[3], p[4])
        else:
            p[0] = ('loop-stmt', p[1], p[2], p[3])
    elif p[4] is not None:
        p[0] = ('loop-stmt', p[2], p[3], p[4])
    else:
        p[0] = ('loop-stmt', p[2], p[3])

def p_label_opt(p):
    '''label_opt :
    | IDENTIFIER COLON'''
    if len(p) == 3:
        p[0] = ('label-opt', p[1])
    else:
        p[0] = None
    
def p_iteration(p):
    '''iteration :
    | WHILE condition
    | iter_part reverse_opt discrete_range'''
    if len(p) == 3:
        p[0] = ('iteration', (p[1], p[2]))
    elif len(p) == 4:
        #p[0] = ('iteration', p[1], p[2], p[3])
        if p[2] is not None:
            p[0] = ('iteration', p[1], p[2], p[3])
        else:
            p[0] = ('iteration', p[1], p[3])
    else:
        p[0] = None
def p_iter_part(p):
    '''iter_part : FOR IDENTIFIER IN'''
    p[0] = ('iter-part', (p[1], p[2]))
def p_reverse_opt(p):
    '''reverse_opt :
    | REVERSE'''
    if len(p) == 2:
        p[0] = ('reverse-opt', p[1])
    else: p[0] = None
    
def p_basic_loop(p):
    '''basic_loop : LOOP statement_s END LOOP'''
    p[0] = ('basic-loop', p[1], p[2])
def p_id_opt(p):
    '''id_opt :
    | designator'''
    if len(p) == 2:
        p[0] = ('id-opt', p[1])
    else:
        p[0] = None
def p_block(p):
    '''block : label_opt block_decl block_body END id_opt SEMICOLON'''
    if p[1] is not None:
        if p[5] is not None:
            p[0] = ('block', p[1], p[2], p[3], p[4], p[5])
        else:
            p[0] = ('block', p[1], p[2], p[3])
    elif p[5] is not None:
        p[0] = ('block', p[2], p[3], p[4], p[5])
    else:
        p[0] = ('block', p[2], p[3])
            
def p_block_decl(p):
    '''block_decl :
    | DECLARE decl_part'''
    if len(p) == 3:
        p[0] = ('block-decl', p[2])
    else:
        p[0] = None

def p_block_body(p):
    '''block_body : BEGIN handled_stmt_s'''
    p[0] = ('block-body', p[1], p[2])
    
def p_handled_stmt_s(p):
    '''handled_stmt_s : statement_s except_handler_part_opt'''
    if p[2] is not None:
        p[0] = ('handled-stmt-s', p[1], p[2])
    else: p[0] = ('handled-stmt-s', p[1])
    
def p_except_handler_part_opt(p):
    '''except_handler_part_opt :
    | except_handler_part'''
    pass
def p_exit_stmt(p):
    '''exit_stmt : EXIT name_opt when_opt SEMICOLON'''
    
    if p[2] is not None:
        if p[3] is not None:
            p[0] = ('exit-stmt', p[1], p[2], p[3])
        else:
            p[0] = ('exit-stmt', p[1], p[2])
    elif p[3] is not None:
        p[0] = ('exit-stmt', p[1], p[3])
    else:
        p[0] = ('exit-stmt', p[1])

def p_name_opt(p):
    '''name_opt :
    | name'''
    if len(p) == 2:
        p[0] = ('name-opt', p[1])
    else:
        p[0] = None
        
def p_when_opt(p):
    '''when_opt :
    | WHEN condition'''
    if len(p) == 3:
        p[0] = ('when-opt', p[2])
    else:
        p[0] = None
def p_return_stmt(p):
    '''return_stmt : RETURN SEMICOLON
    | RETURN expression SEMICOLON'''
    if len(p) == 3:
        p[0] = ('return-stmt', p[1])
    else:
        p[0] = ('return-stmt', p[1], p[2])

def p_goto_stmt(p):
    '''goto_stmt : GOTO name SEMICOLON'''
    p[0] = ('goto-stmt', p[1], p[2])
    
def p_subprog_decl(p):
    '''subprog_decl : subprog_spec SEMICOLON
    | generic_subp_inst SEMICOLON
    | subprog_spec_is_push ABSTRACT SEMICOLON'''
    if DEBUG: print "subprog-decl Called"
    if len(p) == 3:
        p[0] = ('subprog-decl', p[1])
    
def p_subprog_spec(p):
    '''subprog_spec : PROCEDURE compound_name formal_part_opt
    | FUNCTION designator formal_part_opt RETURN name
    | FUNCTION designator '''
    if DEBUG: print "subprog-spec called"
    n = len(p)
    if n == 4:
        if p[3] is not None:
            p[0] = ('subprog-spec', p[2], p[3])
        else:
            p[0] = ('subprog-spec', p[2])
    elif n == 5:
        if p[3] is not None:
            p[0] = ('subprog-spec',  p[2], p[3], p[5])
        else:
            p[0] = ('subprog-spec', p[2], p[5])
    else:
        p[0] = ('subprog-spec', p[2])
        
def p_designator(p):
    '''designator : compound_name
    | STRING'''
    p[0] = ('designator', p[1])
    
def p_formal_part_opt(p):
    '''formal_part_opt : 
    | formal_part'''
    if len(p) == 2:
        p[0] = ('formal-part-opt', p[1])
    else:
        p[0] = None

def p_formal_part(p):
    '''formal_part : LPAREN param_s RPAREN'''
    p[0] = ('formal-part', p[2])
def p_param_s(p):
    '''param_s : param
    | param_s SEMICOLON param'''
    if len(p) == 2:
        p[0] = ('param-s', p[1])
    else:
        p[0] = ('param-s', p[1], p[3])

def p_param(p):
    '''param : def_id_s COLON mode mark init_opt
    | error'''
    if len(p) == 6:
        p[0] = ('param', p[1], p[3], p[4], p[5])
    else:
        p[0] = ('param', p[1])
        
def p_mode(p):
    '''mode :
    | IN
    | OUT
    | IN OUT
    | ACCESS'''
    if len(p) == 2:
        p[0] = ('mode', p[1])
    elif len(p) == 3:
        p[0] = ('mode', (p[1], p[2]))
    else:
        p[0] = None
        
def p_subprog_spec_is_push(p):
    '''subprog_spec_is_push : subprog_spec IS'''
    p[0] = ('subprog-spec-is-push', p[1])
    
def p_subprog_body(p):
    '''subprog_body : subprog_spec_is_push decl_part block_body END id_opt SEMICOLON'''
    if DEBUG: print "subprog-body called"
    if p[5] is not None:
        p[0] = ('subprog-body', p[1], p[2], p[3], ('end', p[5]))
    else: p[0] = ('subprog-body', p[1], p[2], p[3])
    
def p_procedure_call(p):
    '''procedure_call : name SEMICOLON'''
    pass
def p_pkg_decl(p):
    '''pkg_decl : pkg_spec SEMICOLON
    | generic_pkg_inst SEMICOLON'''
    pass
def p_pkg_spec(p):
    '''pkg_spec : PACKAGE compound_name IS decl_item_s private_part END c_id_opt'''
    pass
def p_private_part(p):
    '''private_part :
    | PRIVATE decl_item_s'''
    pass
def p_c_id_opt(p):
    '''c_id_opt : 
    | compound_name'''
    pass
def p_pkg_body(p):
    '''pkg_body : PACKAGE BODY compound_name IS decl_part body_opt END c_id_opt SEMICOLON'''
    pass
def p_body_opt(p):
    '''body_opt :
    | block_body'''
    pass
def p_private_type(p):
    '''private_type : tagged_opt limited_opt PRIVATE'''
    pass
def p_limited_opt(p):
    '''limited_opt :
    | LIMITED'''
    pass
def p_use_clause(p):
    '''use_clause : USE name_s SEMICOLON
    | USE TYPE name_s SEMICOLON'''
    pass
def p_name_s(p):
    '''name_s : name
    | name_s COMMA name'''
    pass
def p_rename_decl(p):
    '''rename_decl : def_id_s COLON object_qualifier_opt subtype_ind renames SEMICOLON
    | def_id_s COLON EXCEPTION renames SEMICOLON
    | rename_unit'''
    pass
def p_rename_unit(p):
    '''rename_unit : PACKAGE compound_name renames SEMICOLON
    | subprog_spec renames SEMICOLON
    | generic_formal_part PACKAGE compound_name renames SEMICOLON
    | generic_formal_part subprog_spec renames SEMICOLON'''
    pass
def p_renames(p):
    '''renames : RENAMES name'''
    pass
def p_task_decl(p):
    '''task_decl : task_spec SEMICOLON'''
    pass
def p_task_spec(p):
    '''task_spec : TASK simple_name task_def
    | TASK TYPE simple_name discrim_part_opt task_def'''
    pass
def p_task_def(p):
    '''task_def :
    | IS entry_decl_s rep_spec_s task_private_opt END id_opt'''
    pass
def p_task_private_opt(p):
    '''task_private_opt :
    | PRIVATE entry_decl_s rep_spec_s'''
    pass
def p_task_body(p):
    '''task_body : TASK BODY simple_name IS decl_part block_body END id_opt SEMICOLON'''
    pass
def p_prot_decl(p):
    '''prot_decl : prot_spec SEMICOLON'''
    pass
def p_prot_spec(p):
    '''prot_spec : PROTECTED IDENTIFIER prot_def
    | PROTECTED TYPE simple_name discrim_part_opt prot_def'''
    pass
def p_prot_def(p):
    '''prot_def : IS prot_op_decl_s prot_private_opt END id_opt'''
    pass
def p_prot_private_opt(p):
    '''prot_private_opt :
    | PRIVATE prot_elem_decl_s '''
    pass
def p_prot_op_decl_s(p):
    '''prot_op_decl_s : 
    | prot_op_decl_s prot_op_decl'''
    pass

def p_prot_op_decl(p):
    '''prot_op_decl : entry_decl
    | subprog_spec SEMICOLON
    | rep_spec
    | pragma'''
    pass
def p_prot_elem_decl_s(p):
    '''prot_elem_decl_s : 
    | prot_elem_decl_s prot_elem_decl'''
    pass
def p_prot_elem_decl(p):
    '''prot_elem_decl : prot_op_decl 
    | comp_decl'''
    pass
def p_prot_body(p):
    '''prot_body : PROTECTED BODY simple_name IS prot_op_body_s END id_opt SEMICOLON'''
    pass
def p_prot_op_body_s(p):
    '''prot_op_body_s : pragma_s
    | prot_op_body_s prot_op_body pragma_s'''
    pass
def p_prot_op_body(p):
    '''prot_op_body : entry_body
    | subprog_body
    | subprog_spec SEMICOLON'''
    pass
def p_entry_decl_s(p):
    '''entry_decl_s : pragma_s
    | entry_decl_s entry_decl pragma_s'''
    pass
def p_entry_decl(p):
    '''entry_decl : ENTRY IDENTIFIER formal_part_opt SEMICOLON
    | ENTRY IDENTIFIER LPAREN discrete_range RPAREN formal_part_opt SEMICOLON'''
    pass
def p_entry_body(p):
    '''entry_body : ENTRY IDENTIFIER formal_part_opt WHEN condition entry_body_part
    | ENTRY IDENTIFIER LPAREN iter_part discrete_range RPAREN formal_part_opt WHEN condition entry_body_part'''
    pass
def p_entry_body_part(p):
    '''entry_body_part : SEMICOLON
    | IS decl_part block_body END id_opt SEMICOLON'''
    pass
def p_rep_spec_s(p):
    '''rep_spec_s :
    | rep_spec_s rep_spec pragma_s'''
    pass
def p_entry_call(p):
    '''entry_call : procedure_call'''
    pass
def p_accept_stmt(p):
    '''accept_stmt : accept_hdr SEMICOLON
    | accept_hdr DO handled_stmt_s END id_opt SEMICOLON'''
    pass
def p_accept_hdr(p):
    '''accept_hdr : ACCEPT entry_name formal_part_opt'''
    pass
def p_entry_name(p):
    '''entry_name : simple_name
    | entry_name LPAREN expression RPAREN'''
    pass
def p_delay_stmt(p):
    '''delay_stmt : DELAY expression SEMICOLON
    | DELAY UNTIL expression SEMICOLON'''
    pass
def p_select_stmt(p):
    '''select_stmt : select_wait
    | async_select
    | timed_entry_call
    | cond_entry_call'''
    pass
def p_select_wait(p):
    '''select_wait : SELECT guarded_select_alt or_select else_opt END SELECT SEMICOLON'''
    pass
def p_guarded_select_alt(p):
    '''guarded_select_alt : select_alt
    | WHEN condition ARROW select_alt'''
    pass
def p_or_select(p):
    '''or_select :
    | or_select OR guarded_select_alt'''
    pass
def p_select_alt(p):
    '''select_alt : accept_stmt stmts_opt
    | delay_stmt stmts_opt
    | TERMINATE SEMICOLON'''
    pass

def p_delay_or_entry_alt(p):
    '''delay_or_entry_alt : delay_stmt stmts_opt
    | entry_call stmts_opt'''
    pass

def p_async_select(p):
    '''async_select : SELECT delay_or_entry_alt THEN ABORT statement_s END SELECT SEMICOLON'''
    pass

def p_timed_entry_call(p):
    '''timed_entry_call : SELECT entry_call stmts_opt OR delay_stmt stmts_opt END SELECT SEMICOLON'''
    pass
def p_cond_entry_call(p):
    '''cond_entry_call : SELECT entry_call stmts_opt ELSE statement_s END SELECT SEMICOLON'''
    pass

def p_stmts_opt(p):
    '''stmts_opt :
    | statement_s'''
    pass
def p_abort_stmt(p):
    '''abort_stmt : ABORT name_s SEMICOLON'''
    pass
def p_compilation(p):
    '''compilation :
    | compilation comp_unit
    | pragma pragma_s'''
    if len(p) == 3:
        p[0] = ('compilation', p[2])

def p_comp_unit(p):
    '''comp_unit : context_spec private_opt unit pragma_s
    | private_opt unit pragma_s'''
    if len(p) == 5:
        p[0] = ('comp-unit', p[1], p[2], p[3], p[4])
    else:
        if p[1] is not None:
            if p[3] is not None:
                p[0] = ('comp-unit', p[1], p[2], p[3])
            else:
                p[0] = ('comp-unit', p[1], p[2])
        else:
            p[0] = ('comp-unit', p[2])
            
def p_private_opt(p):
    '''private_opt :
    | PRIVATE'''
    if len(p) == 2:
        p[0] = ('private-opt', p[1])
    else:
        p[0] = None

def p_context_spec(p):
    '''context_spec : with_clause use_clause_opt
    | context_spec with_clause use_clause_opt
    | context_spec pragma'''
    pass
def p_with_clause(p):
    '''with_clause : WITH c_name_list SEMICOLON'''
    pass
def p_use_clause_opt(p):
    '''use_clause_opt :
    | use_clause_opt use_clause'''
    pass
def p_unit(p):
    '''unit : pkg_decl
    | pkg_body
    | subprog_decl
    | subprog_body
    | subunit
    | generic_decl
    | rename_unit'''
    if DEBUG: print "unit called"
    p[0] = ('unit', p[1])

def p_subunit(p):
    '''subunit : SEPARATE LPAREN compound_name RPAREN subunit_body'''
    pass
def p_subunit_body(p):
    '''subunit_body : subprog_body
    | pkg_body
    | task_body
    | prot_body'''
    pass
def p_body_stub(p):
    '''body_stub : TASK BODY simple_name IS SEPARATE SEMICOLON
    | PACKAGE BODY compound_name IS SEPARATE SEMICOLON
    | subprog_spec IS SEPARATE SEMICOLON
    | PROTECTED BODY simple_name IS SEPARATE SEMICOLON'''
    pass
def p_exception_decl(p):
    '''exception_decl : def_id_s COLON EXCEPTION SEMICOLON'''
    pass
def p_except_handler_part(p):
    '''except_handler_part : EXCEPTION exception_handler
    | except_handler_part exception_handler'''
    pass
def p_exception_handler(p):
    '''exception_handler : WHEN except_choice_s ARROW statement_s
    | WHEN IDENTIFIER COLON except_choice_s ARROW statement_s'''
    pass
def p_except_choice_s(p):
    '''except_choice_s : except_choice
    | except_choice_s '|' except_choice'''
    pass
def p_except_choice(p):
    '''except_choice : name
    | OTHERS'''
    pass
def p_raise_stmt(p):
    '''raise_stmt : RAISE name_opt SEMICOLON'''
    pass
def p_requeue_stmt(p):
    '''requeue_stmt : REQUEUE name SEMICOLON
    | REQUEUE name WITH ABORT SEMICOLON'''
    pass
def p_generic_decl(p):
    '''generic_decl : generic_formal_part subprog_spec SEMICOLON
    | generic_formal_part pkg_spec SEMICOLON'''
    pass
def p_generic_formal_part(p):
    '''generic_formal_part : GENERIC
    | generic_formal_part generic_formal'''
    pass
def p_generic_formal(p):
    '''generic_formal : param SEMICOLON
    | TYPE simple_name generic_discrim_part_opt IS generic_type_def SEMICOLON
    | WITH PROCEDURE simple_name formal_part_opt subp_default SEMICOLON
    | WITH FUNCTION designator formal_part_opt RETURN name subp_default SEMICOLON
    | WITH PACKAGE simple_name IS NEW name LPAREN BOX RPAREN SEMICOLON
    | WITH PACKAGE simple_name IS NEW name SEMICOLON
    | use_clause'''
    pass
def p_generic_discrim_part_opt(p):
    '''generic_discrim_part_opt :
    | discrim_part
    | LPAREN BOX RPAREN'''
    pass
def p_subp_default(p):
    '''subp_default :
    | IS name
    | IS BOX'''
    pass
def p_generic_type_def(p):
    '''generic_type_def : LPAREN BOX RPAREN
    | RANGE BOX
    | MOD BOX
    | DELTA BOX
    | DELTA BOX DIGITS BOX
    | DIGITS BOX
    | array_type
    | access_type
    | private_type
    | generic_derived_type'''
    pass
def p_generic_derived_type(p):
    '''generic_derived_type : NEW subtype_ind
    | NEW subtype_ind WITH PRIVATE
    | ABSTRACT NEW subtype_ind WITH PRIVATE'''
    pass
def p_generic_subp_inst(p):
    '''generic_subp_inst : subprog_spec IS generic_inst'''
    pass
def p_generic_pkg_inst(p):
    '''generic_pkg_inst : PACKAGE compound_name IS generic_inst'''
    pass
def p_generic_inst(p):
    '''generic_inst : NEW name'''
    pass
def p_rep_spec(p):
    '''rep_spec : attrib_def
    | record_type_spec
    | address_spec'''
    pass
def p_attrib_def(p):
    '''attrib_def : FOR mark USE expression SEMICOLON'''
    pass
def p_record_type_spec(p):
    '''record_type_spec : FOR mark USE RECORD align_opt comp_loc_s END RECORD SEMICOLON'''
    pass
def p_align_opt(p):
    '''align_opt :
    | AT MOD expression SEMICOLON'''
    pass
def p_comp_loc_s(p):
    '''comp_loc_s :
    | comp_loc_s mark AT expression RANGE range SEMICOLON'''
    pass
def p_address_spec(p):
    '''address_spec : FOR mark USE AT expression SEMICOLON'''
    pass
def p_code_stmt(p):
    '''code_stmt : qualified SEMICOLON'''
    pass

def p_empty(t):
    'empty : '
    pass

def p_error(p):
    if p:
        print("Syntax error at '%s'" % p.value)
    else:
        print("Syntax error at EOF")
    

yacc = yacc.yacc()
cu = '''
function Levenshtein(Left, Right : String) return Natural is
    D : array(0 .. Left'Last, 0 .. Right'Last) of Natural;
    X : Integer;
  begin
    for I in D'range(1) loop D(I, 0) := I;end loop;
 
    for J in D'range(2) loop D(0, J) := J;end loop;
 
    for I in Left'range loop
      for J in Right'range loop
        D(I, J) := Natural'Min(D(I - 1, J), D(I, J - 1)) + 1;
        D(I, J) := Natural'Min(D(I, J), D(I - 1, J - 1) + Boolean'Pos(Left(I) /= Right(J)));
      end loop;
    end loop;
 
    return D(D'Last(1), D'Last(2));
  end Levenshtein;
'''
program = yacc.parse(cu)
print program
def pprint(tree, depth=0):
    '''
    THis function just converts the tree to "eye-catching" printable string
    '''
    stree = "  "*depth + str(depth) + ""
    for n in tree:
        if isinstance(n, tuple):
            #stree += " {"
            val = pprint(n, depth + 1)
            if val.strip() is not '':
                stree = stree + "\n" + val
                #stree += "\n" + "  "*(depth + 1) + "}"            
        else: stree += " " + str(n)
    return stree
print pprint(program)


