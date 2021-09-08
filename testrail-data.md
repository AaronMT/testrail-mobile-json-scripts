# Testrail Data Encapsulation
[API: Cases - TestRail (gurock.com)](https://www.gurock.com/testrail/docs/api/reference/cases)

### Request filters
```sh
# All test cases for project with ID 1, suite with ID 2 and type_id 3 or 4  
GET index.php?/api/v2/get_cases/1&suite_id=2&type_id=3,4
```
https://testrail.stage.mozaws.net
```
type_id
```

    1. Acceptance
    2. Accessibility
    3. Automated
    4. Compatibility
    5. Destructive
    6. Functional
    7. Other
    8. Performance
    9. Regression
    10. Security
    11. Smoke & Sanity
    12. Usability
    13. Exploratory
    14. End to End

### Automation Status

```
custom_automation_status
```

https://testrail.stage.mozaws.net

```JSON
{
   "id":345222,
   "title":"First launch Home screen UI",
   "section_id":45740,
   "template_id":2,
   "type_id":11,
   "priority_id":2,
   "milestone_id":"None",
   "refs":"firstRunScreenTest",
   "created_by":274,
   "created_on":1558510475,
   "updated_by":81,
   "updated_on":1622119715,
   "estimate":"None",
   "estimate_forecast":"None",
   "suite_id":3192,
   "display_order":1,
   "custom_test_case_owner":4,
   "custom_automation_type":0,
   "custom_automation_status":4,
   "custom_test_objective":"None",
   "custom_preconds":"None",
   "custom_steps":"None",
   "custom_expected":"None",
   "custom_steps_separated":[
      {
         "content":"Install Firefox and launch it.",
         "expected":"Onboarding tour is displayed."
      },
      {
         "content":"Verify the UI.",
         "expected":"Onboarding tour UI contains:\n- Firefox Preview logo and title\n- Private browsing icon (upper-right corner)\n\n- \"Welcome to Firefox!\" greeting,\n- \"Choose your theme\" card,\n- \"Pick your toolbar placement\" card,\n- \"Always-on privacy\" card,\n- \"Sync Firefox between devices\" card,\n- \"Your privacy\" card,\n- \"Start browsing\" button at the bottom of the page.\n\n![](index.php?/attachments/get/19094)\n![](index.php?/attachments/get/19095)\n\n"
      },
      {
         "content":"Redo steps 1 and 2 in landscape mode.",
         "expected":"No issues should be encountered."
      }
   ],
   "custom_notes":"None",
   "custom_mission":"None",
   "custom_goals":"None"
}
```


    1. Untriaged
    2. Suitable
    3. Unsuitable
    4. Completed
    5. Disabled
