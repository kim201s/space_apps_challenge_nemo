using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Networking;

public class BackendCS : MonoBehaviour
{


    [System.Serializable]
    public class FireData
    {
        public int id;

        public float latitude;
        public float longitude;

        public string acq_date;
        public int acq_time;

        public float frp;
        public float brightness;
        public float bright_t31;

        public int hotspot_type;
        public string instrument;
        public string confidence;

        public float scan;
        public float track;

    }

    [System.Serializable]
    public class Root
    {
        public List<FireData> fires;
    }


    private IMarker marker;



    private const string API_URL =
        "https://space-apps-challenge-nemo.onrender.com/fires?min_lon=-90&min_lat=-90&max_lon=90&max_lat=90&date=2026-01-11";

    private void Start()
    {
        marker = ServiceLocator.Current.Get<IMarker>();
        StartCoroutine(GetData());
    }

   private IEnumerator GetData()
{
    while (true)
    {
        using (UnityWebRequest request =
               UnityWebRequest.Get(API_URL))
        {
            yield return request.SendWebRequest();

            if (request.result == UnityWebRequest.Result.Success)
            {
                string json = request.downloadHandler.text;

                Root root = JsonUtility.FromJson<Root>(json);
                 ApplyData(root);
            }
            else
            {
                Debug.LogError("Request failed: " + request.error);
            }
        }

        yield return new WaitForSeconds(10f);
    }
}

    private void ApplyData(Root root)
    {
        foreach(FireData fire in root.fires)
        {
            Debug.Log(fire.latitude + " " + fire.longitude);
            marker.ApplySpot(fire.latitude, fire.longitude);
        }
    }
    // Start is called once before the first execution of Update after the MonoBehaviour is created
   

    // Update is called once per frame
    void Update()
    {
        
    }
}
