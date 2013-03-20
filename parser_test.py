import sys
import lexer
import ply.yacc as yacc

# The token map
tokens = lexer.tokens

# My local symbol table
symTabl = {}


precedence = (
('left', 'PLUS', 'MINUS'),
('left', 'TIMES', 'DIVIDE'),
)
# Grammar description
start = 'goal_symbol'

def p_goal_symbol(p):
    '''goal_symbol : compilation'''
    p[0] = ('goal-symbol', p[1])

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
    pass
def p_object_decl(p):
    '''object_decl : def_id_s COLON object_qualifier_opt object_subtype_def init_opt SEMICOLON'''
    pass
def p_def_id_s(p):
    '''def_id_s : def_id
    | def_id_s COMMA def_id'''
    pass
def p_def_id(p):
    '''def_id  : IDENTIFIER'''
    pass
def p_object_qualifier_opt(p):
    '''object_qualifier_opt :
    | ALIASED
    | CONSTANT
    | ALIASED CONSTANT'''
    pass
def p_object_subtype_def(p):
    '''object_subtype_def : subtype_ind
    | array_type'''
    pass
def p_init_opt(p):
    '''init_opt :
    | IS_ASSIGNED expression'''
    pass
def p_number_decl(p):
    '''number_decl : def_id_s COLON CONSTANT IS_ASSIGNED expression SEMICOLON'''
    pass
def p_type_decl(p):
    '''type_decl : TYPE IDENTIFIER discrim_part_opt type_completion SEMICOLON'''
    pass
def p_discrim_part_opt(p):
    '''discrim_part_opt :
    | discrim_part
    | LPAREN BOX RPAREN'''
    pass
def p_type_completion(p):
    '''type_completion :
    | IS type_def'''
    pass
def p_type_def(p):
    '''type_def : enumeration_type 
    | integer_type
    | real_type
    | array_type
    | record_type
    | access_type
    | derived_type
    | private_type'''
    pass
def p_subtype_decl(p):
    '''subtype_decl : SUBTYPE IDENTIFIER IS subtype_ind SEMICOLON'''
    pass
def p_subtype_ind(p):
    '''subtype_ind : name constraint
    | name'''
    pass
def p_constraint(p):
    '''constraint : range_constraint
    | decimal_digits_constraint'''
    pass
def p_decimal_digits_constraint(p):
    '''decimal_digits_constraint : DIGITS expression range_constr_opt'''
    pass
def p_derived_type(p):
    '''derived_type : NEW subtype_ind
    | NEW subtype_ind WITH PRIVATE
    | NEW subtype_ind WITH record_def
    | ABSTRACT NEW subtype_ind WITH PRIVATE
    | ABSTRACT NEW subtype_ind WITH record_def'''
    pass
def p_range_constraint(p):
    '''range_constraint : RANGE range'''
    pass
def p_range(p):
    '''range : simple_expression DOUBLEDOT simple_expression
    | name TICK RANGE
    | name TICK RANGE LPAREN expression RPAREN'''
    pass

def p_enumeration_type(p):
    '''enumeration_type : LPAREN enum_id_s RPAREN'''
    pass

def p_enum_id_s(p):
    '''enum_id_s : enum_id
    | enum_id_s COMMA enum_id'''
    pass

def p_enum_id(p):
    '''enum_id : IDENTIFIER
    | CHARACTER'''
    pass
def p_integer_type(p):
    '''integer_type : range_spec
    | MOD expression'''
    pass
def p_range_spec(p):
    '''range_spec : range_constraint'''
    pass
def p_range_spec_opt(p):
    '''range_spec_opt :
    | range_spec'''
    pass
def p_real_type(p):
    '''real_type : float_type
    | fixed_type'''
    pass
def p_float_type(p):
    '''float_type : DIGITS expression range_spec_opt'''
    pass
def p_fixed_type(p):
    '''fixed_type : DELTA expression range_spec
    | DELTA expression DIGITS expression range_spec_opt'''
    pass
def p_array_type(p):
    '''array_type : unconstr_array_type
    | constr_array_type'''
    pass
def p_unconstr_array_type(p):
    '''unconstr_array_type : ARRAY LPAREN index_s RPAREN OF component_subtype_def'''
    pass
def p_constr_array_type(p):
    '''constr_array_type : ARRAY iter_index_constraint OF component_subtype_def'''
    pass
def p_component_subtype_def(p):
    '''component_subtype_def : aliased_opt subtype_ind'''
    pass
def p_aliased_opt(p):
    '''aliased_opt : 
    | ALIASED'''
    pass
def p_index_s(p):
    '''index_s : index
    | index_s COMMA index'''
    pass
def p_index(p):
    '''index : name RANGE BOX'''
    pass
def p_iter_index_constraint(p):
    '''iter_index_constraint : LPAREN iter_discrete_range_s RPAREN'''
    pass
def p_iter_discrete_range_s(p):
    '''iter_discrete_range_s : discrete_range
    | iter_discrete_range_s COMMA discrete_range'''
    pass
def p_discrete_range(p):
    '''discrete_range : name range_constr_opt
    | range'''
    pass
def p_range_constr_opt(p):
    '''range_constr_opt :
    | range_constraint'''
    pass
def p_record_type(p):
    '''record_type : tagged_opt limited_opt record_def'''
    pass
def p_record_def(p):
    '''record_def : RECORD   comp_list END RECORD
    | NULL RECORD'''
    pass
def p_tagged_opt(p):
    '''tagged_opt :
    | TAGGED
    | ABSTRACT TAGGED'''
    pass
def p_comp_list(p):
    '''comp_list : comp_decl_s variant_part_opt
    | variant_part  
    | NULL SEMICOLON  '''
    pass
def p_comp_decl_s(p):
    '''comp_decl_s : comp_decl
    | comp_decl_s   comp_decl'''
    pass
def p_variant_part_opt(p):
    '''variant_part_opt :  
    |   variant_part  '''
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
    '''variant_part : CASE simple_name IS   variant_s END CASE SEMICOLON'''
    pass
def p_variant_s(p):
    '''variant_s : variant
    | variant_s variant'''
    pass
def p_variant(p):
    '''variant : WHEN choice_s ARROW   comp_list'''
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
    pass
def p_decl_item_s(p):
    '''decl_item_s : 
    | decl_item_s1'''
    pass
def p_decl_item_s1(p):
    '''decl_item_s1 : decl_item
    | decl_item_s1 decl_item'''
    pass
def p_decl_item(p):
    '''decl_item : decl
    | use_clause
    | rep_spec
    '''
    pass
def p_decl_item_or_body_s1(p):
    '''decl_item_or_body_s1 : decl_item_or_body
    | decl_item_or_body_s1 decl_item_or_body'''
    pass
def p_decl_item_or_body(p):
    '''decl_item_or_body : body
    | decl_item'''
    pass
def p_body(p):
    '''body : subprog_body
    | pkg_body
    | task_body
    | prot_body'''
    pass
def p_name(p):
    '''name : simple_name
    | indexed_comp
    | selected_comp
    | attribute
    | operator_symbol'''
    pass
def p_mark(p):
    '''mark : simple_name
    | mark TICK attribute_id
    | mark DOT simple_name'''
    pass
def p_simple_name(p):
    '''simple_name : IDENTIFIER'''
    pass
def p_compound_name(p):
    '''compound_name : simple_name
    | compound_name DOT simple_name'''
    pass
def p_c_name_list(p):
    '''c_name_list : compound_name
     | c_name_list COMMA compound_name'''
    pass
def p_used_char(p):
    '''used_char : CHARACTER'''
    pass
def p_operator_symbol(p):
    '''operator_symbol : STRING'''
    pass
def p_indexed_comp(p):
    '''indexed_comp : name LPAREN value_s RPAREN'''
    pass
def p_value_s(p):
    '''value_s : value
    | value_s COMMA value'''
    pass
def p_value(p):
    '''value : expression
    | comp_assoc
    | discrete_with_range
    | error'''
    pass
def p_selected_comp(p):
    '''selected_comp : name DOT simple_name
    | name DOT used_char
    | name DOT operator_symbol
    | name DOT ALL'''
    pass
def p_attribute(p):
    '''attribute : name TICK attribute_id'''
    pass
def p_attribute_id(p):
    '''attribute_id : IDENTIFIER
    | DIGITS
    | DELTA
    | ACCESS'''
    pass
def p_literal(p):
    '''literal : NUMBER
    | used_char
    | NULL'''
    pass
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
    pass
def p_comp_assoc(p):
    '''comp_assoc : choice_s ARROW expression'''
    pass
def p_expression(p):
    '''expression : relation
    | expression logical relation
    | expression short_circuit relation'''
    pass
def p_logical(p):
    '''logical : AND
    | OR
    | XOR'''
    pass
def p_short_circuit(p):
    '''short_circuit : AND THEN
    | OR ELSE'''
    pass
def p_relation(p):
    '''relation : simple_expression
    | simple_expression relational simple_expression
    | simple_expression membership range
    | simple_expression membership name'''
    pass
def p_relational(p):
    '''relational : EQ
    | NE
    | LT
    | LE
    | GT
    | GE'''
    pass
def p_membership(p):
    '''membership : IN
    | NOT IN'''
    pass
def p_simple_expression(p):
    '''simple_expression : unary term
    | term
    | simple_expression adding term'''
    pass
def p_unary(p):
    '''unary   : PLUS
    | MINUS'''
    pass
def p_adding(p):
    '''adding  : PLUS
    | MINUS
    | AMPERSAND'''
    pass
def p_term(p):
    '''term    : factor
    | term multiplying factor'''
    pass
def p_multiplying(p):
    '''multiplying : TIMES
    | DIVIDE
    | MOD
    | REM'''
    pass
def p_factor(p):
    '''factor : primary
    | NOT primary
    | ABS primary
    | primary POW primary'''
    pass
def p_primary(p):
    '''primary : literal
    | name
    | allocator
    | qualified
    | parenthesized_primary'''
    pass
def p_parenthesized_primary(p):
    '''parenthesized_primary : aggregate
    | LPAREN expression RPAREN'''
    pass
def p_qualified(p):
    '''qualified : name TICK parenthesized_primary'''
    pass
def p_allocator(p):
    '''allocator : NEW name
    | NEW qualified'''
    pass
def p_statement_s(p):
    '''statement_s : statement
    | statement_s statement'''
    pass
def p_statement(p):
    '''statement : unlabeled
    | label statement'''
    pass
def p_unlabeled(p):
    '''unlabeled : simple_stmt
    | compound_stmt'''
    pass
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
    pass
def p_compound_stmt(p):
    '''compound_stmt : if_stmt
    | case_stmt
    | loop_stmt
    | block
    | accept_stmt
    | select_stmt'''
    pass
def p_label(p):
    '''label : LLB IDENTIFIER RLB'''
    pass
def p_NULL_stmt(p):
    '''NULL_stmt : NULL SEMICOLON'''
    pass
def p_assign_stmt(p):
    '''assign_stmt : name IS_ASSIGNED expression SEMICOLON'''
    pass
def p_if_stmt(p):
    '''if_stmt : IF cond_clause_s else_opt END IF SEMICOLON'''
    pass
def p_cond_clause_s(p):
    '''cond_clause_s : cond_clause
    | cond_clause_s ELSIF cond_clause'''
    pass
def p_cond_clause(p):
    '''cond_clause : cond_part statement_s'''
    pass
def p_cond_part(p):
    '''cond_part : condition THEN'''
    pass
def p_condition(p):
    '''condition : expression'''
    pass
def p_else_opt(p):
    '''else_opt :
    | ELSE statement_s'''
    pass
def p_case_stmt(p):
    '''case_stmt : case_hdr   alternative_s END CASE SEMICOLON'''
    pass
def p_case_hdr(p):
    '''case_hdr : CASE expression IS'''
    pass
def p_alternative_s(p):
    '''alternative_s :
    | alternative_s alternative'''
    pass
def p_alternative(p):
    '''alternative : WHEN choice_s ARROW statement_s'''
    pass
def p_loop_stmt(p):
    '''loop_stmt : label_opt iteration basic_loop id_opt SEMICOLON'''
    pass
def p_label_opt(p):
    '''label_opt :
    | IDENTIFIER COLON'''
    pass
def p_iteration(p):
    '''iteration :
    | WHILE condition
    | iter_part reverse_opt discrete_range'''
    pass
def p_iter_part(p):
    '''iter_part : FOR IDENTIFIER IN'''
    pass
def p_reverse_opt(p):
    '''reverse_opt :
    | REVERSE'''
    pass
def p_basic_loop(p):
    '''basic_loop : LOOP statement_s END LOOP'''
    pass
def p_id_opt(p):
    '''id_opt :
    | designator'''
    pass
def p_block(p):
    '''block : label_opt block_decl block_body END id_opt SEMICOLON'''
    pass
def p_block_decl(p):
    '''block_decl :
    | DECLARE decl_part'''
    pass
def p_block_body(p):
    '''block_body : BEGIN handled_stmt_s'''
    pass
def p_handled_stmt_s(p):
    '''handled_stmt_s : statement_s except_handler_part_opt'''
    pass
def p_except_handler_part_opt(p):
    '''except_handler_part_opt :
    | except_handler_part'''
    pass
def p_exit_stmt(p):
    '''exit_stmt : EXIT name_opt when_opt SEMICOLON'''
    pass
def p_name_opt(p):
    '''name_opt :
    | name'''
    pass
def p_when_opt(p):
    '''when_opt :
    | WHEN condition'''
    pass
def p_return_stmt(p):
    '''return_stmt : RETURN SEMICOLON
    | RETURN expression SEMICOLON'''
    pass
def p_goto_stmt(p):
    '''goto_stmt : GOTO name SEMICOLON'''
    pass
def p_subprog_decl(p):
    '''subprog_decl : subprog_spec SEMICOLON
    | generic_subp_inst SEMICOLON
    | subprog_spec_is_push ABSTRACT SEMICOLON'''
    pass
def p_subprog_spec(p):
    '''subprog_spec : PROCEDURE compound_name formal_part_opt
    | FUNCTION designator formal_part_opt RETURN name
    | FUNCTION designator '''
    pass
def p_designator(p):
    '''designator : compound_name
    | STRING'''
    pass
def p_formal_part_opt(p):
    '''formal_part_opt : 
    | formal_part'''
    pass
def p_formal_part(p):
    '''formal_part : LPAREN param_s RPAREN'''
    pass
def p_param_s(p):
    '''param_s : param
    | param_s SEMICOLON param'''
    pass
def p_param(p):
    '''param : def_id_s COLON mode mark init_opt
    | error'''
    pass
def p_mode(p):
    '''mode :
    | IN
    | OUT
    | IN OUT
    | ACCESS'''
    pass
def p_subprog_spec_is_push(p):
    '''subprog_spec_is_push : subprog_spec IS'''
    pass
def p_subprog_body(p):
    '''subprog_body : subprog_spec_is_push decl_part block_body END id_opt SEMICOLON'''
    pass
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
    | rep_spec'''
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
    '''prot_op_body_s :  
    | prot_op_body_s prot_op_body  '''
    pass
def p_prot_op_body(p):
    '''prot_op_body : entry_body
    | subprog_body
    | subprog_spec SEMICOLON'''
    pass
def p_entry_decl_s(p):
    '''entry_decl_s :  
    | entry_decl_s entry_decl  '''
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
    | rep_spec_s rep_spec  '''
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
    '''
    if len(p) == 3:
        if p[1] is not None and p[2] is not None:
            p[0] = p[1] + p[2]
        elif p[2] is not None:
            p[0] = p[2]
    else:
        p[0] = None

def p_comp_unit(p):
    '''comp_unit : context_spec private_opt unit
    | private_opt unit '''
    if len(p) == 4:
        p[0] = ('comp-unit', p[1], p[2], p[3])
    else: p[0] = ('comp-unit', p[1], p[2])
    
def p_private_opt(p):
    '''private_opt :
    | PRIVATE'''
    pass
def p_context_spec(p):
    '''context_spec : with_clause use_clause_opt
    | context_spec with_clause use_clause_opt
    | context_spec '''
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
    pass
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
print yacc.parse(cu)
