<?php

/**
 * Plugin Name: PDB Generate Member ID
 * Description: Provides a unique ID for new signups and new records in Participants Database
 * Author: Roland Barker (xnau), Customisation (start_value at 1000000 + generate ID when importing csv) by Fafadji GNOFAME. (Base code found here : https://xnau.com/generating-unique-member-ids-for-new-registrations/)
 * Version: 1.1.0
 */
class pdb_generate_member_id {

  /**
   * @var string name of the member id field
   */
  private $id_field = 'member_id';

  /**
   * @var string the starting member ID value
   */
  private $start_value = 100000;

  /**
   * initializes the plugin, setting up our filters
   */
  public function __construct()
  {
    // this is used when a signup form is submitted
    add_filter( 'pdb-before_submit_signup', array($this, 'generate_new_member_id') );

    // this is used when a new record is added from the backend
    add_filter( 'pdb-before_submit_add', array($this, 'generate_new_member_id') );
    
    // this is used when a record is updated
    add_filter( 'pdb-before_submit_update', array( $this, 'add_member_id' ) );
    
    // this is used when a record is imported via csv
    add_filter( 'pdb-before_csv_store_record', array( $this, 'set_member_id_field_to_null_on_import' ) );
    add_action( 'pdb-after_import_record', array( $this, 'generate_member_id_on_cnv_import' ), 10, 3 );

    // this hides the field in the signup form
    add_filter( 'pdb-before_field_added_to_iterator', array( $this, 'hide_id_field' ) );
  }

  public function set_member_id_field_to_null_on_import($record) {
    $record[$this->id_field] = null;
    return $record;
  }

  public function generate_member_id_on_cnv_import( $record, $id, $insert_status ) {
    if( $insert_status === 'insert' ) {
        $new_record = $this->generate_new_member_id($record);
        Participants_Db::write_participant($new_record,$id);
        Participants_Db::$insert_status = 'insert';
    } elseif( $insert_status === 'update' ) {
        $new_record = Participants_Db::get_participant($id);
        if($new_record[$this->id_field] === NULL) {
            $new_record = $this->generate_new_member_id($new_record);
            Participants_Db::write_participant($new_record,$id);
        } 
    }
  }


  /**
   * generates the new ID
   * 
   * @param array $record the new record values
   * 
   * @return array of data to post
   */
  public function generate_new_member_id( $record )
  {
    $last_id = $this->last_saved_member_id();

    if ( !$last_id ) {
      // no ids have been saved yet, so we start here
      $last_id = $this->start_value;
    }

    /*
     *  we start the process with the previous ID
     */
    $new_id = $last_id;

    /*
     * this will keep looping until we try a unique ID
     * 
     * as soon as we try a unique one, it will break out of the loop
     */
    while ( $this->member_id_is_not_unique( $new_id ) ) {

      /*
       * this is where we generate the new ID
       * 
       * you could make up your own formula here, for this example we simply increment the value
       */
      $new_id = $new_id + 1;
      
    }
    
    /*
     * we have our new ID, add it to the data to be saved
     */
    $record[$this->id_field] = $new_id;

    // the data goes back to the main plugin to be saved
    return $record;
  }
  
  /**
   * checks an existing record for an ID and supplies one if needed
   * 
   * @param array $record the submitted data
   * @return array the data to save
   */
  public function add_member_id( $record )
  {
    // if the updating record doesn't have a member ID, add one
    if ( empty( $record[$this->id_field] ) ) {
      $record = $this->generate_new_member_id($record);
    }
    return $record;
  }
  
  /**
   * hides the id field in the signup form
   * 
   * @param PDb_Field_Item $field the field object
   * @return PDb_Field_Item the field object
   */
  public function hide_id_field( $field )
  {
    if ( $field->module === 'signup' && $field->name === $this->id_field ) {
      // this is the member id field in the signup form, skip it.
      return null;
    }
    return $field;
  }

  /**
   * provides the last entered ID
   * 
   * @global wpdb $wpdb
   */
  private function last_saved_member_id()
  {
    global $wpdb;
    $sql = 'SELECT `' . $this->id_field . '` FROM ' . Participants_Db::$participants_table . ' WHERE `' . $this->id_field . '` IS NOT NULL ORDER BY `' . $this->id_field . '` DESC LIMIT 1';
    return $wpdb->get_var( $sql );
  }

  /**
   * checks for a duplicate ID
   * 
   * @global wodb $wpdb
   * @param string $member_id the id value
   * @return bool true if the value is not unique
   */
  private function member_id_is_not_unique( $member_id )
  {
    global $wpdb;
    $sql = 'SELECT `id` FROM ' . Participants_Db::$participants_table . ' WHERE ' . $this->id_field . ' = "%s"';
    $result = $wpdb->get_col( $wpdb->prepare( $sql, $member_id ) );
    return $wpdb->num_rows !== 0;
  }

}

new pdb_generate_member_id(); // instantiates the class
