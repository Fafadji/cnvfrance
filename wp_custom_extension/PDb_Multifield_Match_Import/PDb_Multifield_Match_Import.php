<?php
/**
 * Plugin Name: PDb Multi-Field Match Import
 * Description: Multiple-field (firt_name, last_name, email) match when a signup form is submitted or importing a CSV to Participants Database.  
 * Author: Roland Barker (xnau), Customisation (match also email + update record without error) by Fafadji GNOFAME. (Base code found here : https://xnau.com/matching-multiple-fields-with-csv-import-or-signup-submission/)    
 * Version: 1.1.0        
*/
class PDb_Multifield_Match_Import {
  
  /**
   * @var array list of fields to match on import
   *
   * set this array to the fields that must match between the incoming data
   * and the database
   */
  private $match_field_list = array( 'first_name', 'last_name', 'email', 'm_source_2018' );
  
  /**
   * @var int this holds the ID of the matched record or int 0 if no match
   */
  private $match_id = 0;
  
  /**
   * sets up our filters
   */
  public function __construct()
  {
    add_filter( 'pdb-incoming_record_match', array( $this, 'check_for_match' ), 10, 4 );
    add_filter( 'pdb-process_form_matched_record', array( $this, 'provide_the_matched_id' ) );
  }
  
  /**
   * checks the incoming data against the database to find a match
   *
   * @param bool $match true if a field match was made using the normal matching (this is ignored)
   * @param array $post the incoming data
   *
   * @return bool true if the record is a match
   */
  public function check_for_match( $match, $post, $duplicate_record_preference, $currently_importing_csv )
  {

    // prevent updating record from matching itself if we are avoiding duplicates
    $mask_id = ($duplicate_record_preference === '2' and isset($post['id'])) ? $post['id'] : 0;

    $match_data =  $this->match_data($post);

    $match_data[] = $mask_id;

    // set the match_id property to the result of our search
    $this->match_id = $this->check_db_for_match( $match_data );
    
    // return true if we have a match
    return $this->match_id !== false;
  }
  
  /**
   * supplies the matched id
   * 
   * @param int $match_id the matched id found by the standard method (we ignore this)
   * 
   * @return int  the matched record ID
   */
  public function provide_the_matched_id( $match_id )
  {
    return $this->match_id;
  }
  
  /**
   * queries the database with the match field data to find a match
   *
   * @global wpdb $wpdb
   * @param array $match_data the data to use in finding the match as $name => $value
   *
   * @return int|bool the record ID if there is a match, bool false if no match
   */
  private function check_db_for_match( $match_data )
  {

    $query = 'SELECT `id` FROM ' . Participants_Db::$participants_table . ' p WHERE ' . $this->where_clause(). ' AND p.id <> %s';
    
    global $wpdb;
    $result = $wpdb->get_col( $wpdb->prepare( $query, $match_data ) );
    
    // add debugging to make sure the query and result is as expected
    if (WP_DEBUG) error_log(__METHOD__.' query: '.$wpdb->last_query.' result: '.print_r($result,1));
    
    // make sure there is only one match, then return the found ID
    if ( count( $result ) === 1 ) {
      return current( $result );
    }
    
    // no match or more than one match
    return false;
  }
  
  /**
   * provides the where clause
   *
   * @return string where clause forthe match query
   */
  private function where_clause()
  {
    $where_clause = array();
    // make an array of all the subclauses
    foreach ( $this->match_field_list as $field ) {
      $where_clause[] = '`' . $field . '` = "%s"';
    }
    // string them all together to build the clause
    return implode( ' AND ', $where_clause);
  }
  
  /**
   * provides the match data array
   * 
   * this extracts the match field data from the posted data
   * 
   * @param array $post the posted data
   * 
   * @return array the extracted data
   */
  private function match_data( $post )
  {
    $match_data = array();
    foreach ( $this->match_field_list as $field ) {
      $match_data[] = isset( $post[$field] ) ? $post[$field] : ''; 
    }
    return $match_data;
  }
  
}

 new PDb_Multifield_Match_Import;
