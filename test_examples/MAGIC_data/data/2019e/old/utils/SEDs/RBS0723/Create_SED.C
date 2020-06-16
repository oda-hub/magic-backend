//////////////////////////////////
//   Plot Broadband SED         //
//   Cornelia Arcaro Jan  2019  //
//////////////////////////////////

#include <TCanvas.h>
#include <TH2F.h>
#include <TGraphAsymmErrors.h>
#include <TString.h>
#include <TStyle.h>

#include <fstream>
#include <iostream>
#include <stdio.h>

using namespace std;

// dat1: data to model
// dat2: archival data
// dat3: modelling curve of the broad-band SED data with the following format: freq, flux: FABRIZIO
// dat4: modelling curve of the broad-band SED data with the following format: freq, flux: KATSUAKI
// dat51: modelling curve of the broad-band SED data with the following format: freq, flux: MATTEO SS
// dat52: modelling curve of the broad-band SED data with the following format: freq, flux: MATTEO PSS
// dat53: modelling curve of the broad-band SED data with the following format: freq, flux: MATTEO NEU

void Create_SED(TString dat1="RBS0723_mwl_data.dat",TString dat2="RBS0723_mwl_data_hystorical.dat",TString dat3="0723_model_SL_correct_units_Fab.dat",TString dat4="0723_model_correct_units_Asano.dat",TString dat50="RBS0723_model_ss_correct_units_Matteo.dat", TString dat51="RBS0723_model_pss_correct_units_Matteo.dat",TString dat52="RBS0723_model_neu3_correct_units_Matteo.dat")
{
    Float_t factor=4.13566553853599E-15;
    ////////////////////
    //DRAWING SESSION//
    ///////////////////
    
    TCanvas *c1 = new TCanvas("c1","SED",600,600);
    c1->SetFillColor(10);
    //c1->SetBorderMode(0);
    //c1->SetBorderSize(1);
    c1->SetLeftMargin(0.11);
    c1->SetRightMargin(0.03);
    //c1->SetTopMargin(0.118943);
    //c1->SetBottomMargin(0.160793);
    //c1->SetFrameBorderMode(0);
    c1->SetFrameFillColor(0);
    c1->SetFrameLineWidth(1);
    c1->SetLogx();
    c1->SetLogy();
    
    gStyle->SetOptStat(0);
    //  TH2F *h = new TH2F("h","",200,9,28.5,200,-19.5,-10.5);
    Double_t xmin=1e9;
    Double_t xmax=5e34;
    Double_t ymin=1e-16;
    Double_t ymax=1e-10;
    TH2F *h = new TH2F("h","",200,xmin,xmax,200,ymin,ymax);
    h->SetTitle("RBS 0723");
    h->SetXTitle("#nu [Hz]");
    h->GetXaxis()->SetNdivisions(509);
    h->GetYaxis()->SetTitleOffset(1.55);
    h->GetXaxis()->SetTitleOffset(1.2);
    h->SetYTitle("#nuf(#nu) [ergs cm^{-2} s^{-1}]");
    h->Draw();
    
    // Additional x-axis on top of canvas in energy
    TGaxis *Xaxis = new TGaxis(h->GetXaxis()->GetXmin(),h->GetYaxis()->GetXmax(),h->GetXaxis()->GetXmax(),h->GetYaxis()->GetXmax(),h->GetXaxis()->GetXmin()*factor,h->GetXaxis()->GetXmax()*factor,509,"-G");
    // Xaxis->SetTickSize(0.02);
    Xaxis->SetLabelFont(42);
    Xaxis->SetLabelOffset(0.005);
    Xaxis->SetLabelSize( 0.035  );
    Xaxis->SetTitleFont(42);
    Xaxis->SetTitleSize( 0.035  );
    Xaxis->SetTitle("E [eV]");
    Xaxis->Draw();
    
/////////////////////////
//SECTION TO READ IN DATA
/////////////////////////
    Int_t symb[5]={22,23,24,25,26};
    char inst[5][7]={"UVOT","XRT","NuSTAR","Fermi","MAGIC"};
//File dat1 should contain the modeled broad-band SED data with the following format: id ,freq, freq_lower_err, freq_upper_err, flux, flux_lower_err, flux_upper_err
    Int_t id;
    Int_t i=0;
    Int_t id_old=1;
    Float_t nu,nu_errl,nu_errh,flux, flux_errl,flux_errh;
    TString line;
    std::ifstream In1;
    //TGraphAsymmErrors* gr1 = new TGraphAsymmErrors(dat1.Data());
    TGraphAsymmErrors* gr1 = new TGraphAsymmErrors();
    if (dat1 == ""){
        cout<<"FILE 1 NOT DEFINED....SKIPPING IT"<<endl;
    }
    else{
         In1.open(dat1);
        if(!(In1)){
            cout<<"FILE "<<dat1.Data()<<" WAS NOT FOUND"<<endl;
            return;
        }
        else{
            cout<<"READING FILE "<<dat1.Data()<<" ..."<<endl;
	    
            while(!In1.eof()) {
                    line.ReadLine(In1);
                    if((line.BeginsWith("/")) || (line.BeginsWith("!"))){
                        continue;
                    }
                    if(sscanf((const char *)line,"%i %f %f %f %f %f %f",&id, &nu, &nu_errl,&nu_errh, &flux, &flux_errl, &flux_errh)==7){
                        if(flux_errl !=0 && flux_errh !=0){
                            if(id_old == id){
                                gr1->SetPoint(i,nu,flux);
                                //gr1->SetPointError(i,nu_errl,nu_errh,flux_errl,flux_errh);
                                gr1->SetPointError(i,0,0,flux_errl,flux_errh);
                                i++;
                            }
                            else{
                                cout<<"PLOTTING "<<inst[id_old-1]<<" DATA"<<endl;
                                gr1->SetMarkerStyle(symb[id_old-1]);
                                gr1->SetMarkerColor(kRed);
                                gr1->SetLineColor(kRed);
                                gr1->Draw("p same");
                                i=0;
                                id_old=id;
				//   gr1 = new TGraphAsymmErrors(dat1.Data());
                                gr1 = new TGraphAsymmErrors();
                                gr1->SetPoint(i,nu,flux);
                                //gr1->SetPointError(i,nu_errl,nu_errh,flux_errl,flux_errh);
                                gr1->SetPointError(i,0,0,flux_errl,flux_errh);
                                i++;
                            }
                        }
                        else{
                            TLine *arrl=new TLine(nu-nu_errl,flux,nu+nu_errh,flux);
                            arrl->SetLineColor(kRed);
                            arrl->Draw();
                            TArrow *arr= new TArrow(nu,flux,nu,flux-flux*0.5,0.02,"|>");
                            arr->SetFillColor(kRed);
                            arr->SetLineColor(kRed);
                            arr->Draw();
                        }
                    
                    }
                    else{
                        cout << "FILE "<<dat1.Data()<<" COULD NOT BE READ!" << endl;
                        return;
                }
            }
            cout<<"PLOTTING "<<inst[id_old-1]<<" DATA"<<endl;
            gr1->SetMarkerStyle(symb[id_old-1]);
            gr1->SetMarkerColor(kRed);
            gr1->SetLineColor(kRed);
            gr1->Draw("p same");
        }
    }
    //File dat2 should contain archival data of the broad-band SED data with the following format: freq, freq_lower_err, freq_upper_err, flux, flux_lower_err, flux_upper_err
    std::ifstream In2;
    // TGraphAsymmErrors* gr2 = new TGraphAsymmErrors(dat2.Data());//elisa
    TGraphAsymmErrors* gr2 = new TGraphAsymmErrors();
    i=0;
    if (dat2 == ""){
        cout<<"FILE 2 NOT DEFINED....SKIPPING IT"<<endl;
    }
    else{
        In2.open(dat2);
        if(!(In2)){
            cout<<"FILE "<<dat2.Data()<<" WAS NOT FOUND"<<endl;
            return;
        }
        else{
            cout<<"READING FILE "<<dat2.Data()<<" ..."<<endl;
	   
            while(!In2.eof()) {
                line.ReadLine(In2);
                if((line.BeginsWith("/")) || (line.BeginsWith("!"))){
                    continue;
                }
                if(sscanf((const char *)line,"%f %f %f %f %f %f", &nu, &nu_errl,&nu_errh, &flux, &flux_errl, &flux_errh)==6){
                    gr2->SetPoint(i,nu,flux);
                    gr2->SetPointError(i,nu_errl,nu_errh,flux_errl,flux_errh);
                    i++;
                }
                else{
                    cout << "FILE "<<dat2.Data()<<" COULD NOT BE READ!" << endl;
                    return;
                }
                gr2->SetLineColor(kGray);
                gr2->SetMarkerColor(kGray);
                gr2->SetMarkerStyle(22);
                gr2->Draw("p same");
            }
        }
    }
     //File dat3 should contain a modelling curve of the broad-band SED data with the following format: freq, flux,
    std::ifstream In3;
    // TGraph* gr3 = new TGraph(dat3.Data());
    TGraph* gr3 = new TGraph();
    i=0;
    if (dat3 == ""){
        cout<<"FILE 3 NOT DEFINED....SKIPPING IT"<<endl;
    }
    else{
        In3.open(dat3);
        if(!(In3)){
            cout<<"FILE "<<dat3.Data()<<" WAS NOT FOUND"<<endl;
            return;
        }
        else{
            cout<<"READING FILE "<<dat3.Data()<<" ..."<<endl;
         
            while(!In3.eof()) {
                line.ReadLine(In3);
                if((line.BeginsWith("/")) || (line.BeginsWith("!"))){
                    continue;
                }
                if(sscanf((const char *)line,"%f %f", &nu, &flux)==2){
                    gr3->SetPoint(i,nu,flux);
                    i++;
                }
                else{
                    cout << "FILE "<<dat3.Data()<<" COULD NOT BE READ!" << endl;
                    return;
                }
            }
            gr3->SetLineColor(kBlack);
            gr3->SetLineStyle(1);
            gr3->SetLineWidth(2);
            gr3->Draw("l same");
        }
    }
    //File dat4 should contain a modelling curve of the broad-band SED data with the following format: freq, flux,
    std::ifstream In4;
    // TGraph* gr4 = new TGraph(dat4.Data());
    TGraph* gr4 = new TGraph();
    i=0;
    if (dat4 == ""){
        cout<<"FILE 4 NOT DEFINED....SKIPPING IT"<<endl;
    }
    else{
        In4.open(dat4);
        if(!(In4)){
            cout<<"FILE "<<dat4.Data()<<" WAS NOT FOUND"<<endl;
            return;
        }
        else{
            cout<<"READING FILE "<<dat4.Data()<<" ..."<<endl;
          
            while(!In4.eof()) {
                line.ReadLine(In4);
                if((line.BeginsWith("/")) || (line.BeginsWith("!"))){
                    continue;
                }
                if(sscanf((const char *)line,"%f %f", &nu, &flux)==2){
                    gr4->SetPoint(i,nu,flux);
                    i++;
                }
                else{
                    cout << "FILE "<<dat4.Data()<<" COULD NOT BE READ!" << endl;
                    return;
                }
            }
            gr4->SetLineColor(kBlue);
            gr4->SetLineStyle(2);
            gr4->SetLineWidth(2);
            gr4->Draw("l same");
        }
    }
    // PROTON SYNCHRO MODEL   
    //File dat5 should contain a modelling curve of the broad-band SED data with the following format: freq, flux,
    std::ifstream In50;
    //  TGraph* gr5 = new TGraph(dat5.Data());
    TGraph* gr50 = new TGraph();
    i=0;
    if (dat50 == ""){
        cout<<"FILE 50 NOT DEFINED....SKIPPING IT"<<endl;
    }
    else{
        In50.open(dat50);
        if(!(In50)){
            cout<<"FILE "<<dat50.Data()<<" WAS NOT FOUND"<<endl;
            return;
        }
        else{
            cout<<"READING FILE "<<dat50.Data()<<" ..."<<endl;
         
            while(!In50.eof()) {
                line.ReadLine(In50);
                if((line.BeginsWith("/")) || (line.BeginsWith("!"))){
                    continue;
                }
                if(sscanf((const char *)line,"%f %f", &nu, &flux)==2){
                    gr50->SetPoint(i,nu,flux);
                    i++;
                }
                else{
                    cout << "FILE "<<dat50.Data()<<" COULD NOT BE READ!" << endl;
                    return;
                }
            }
            gr50->SetLineColor(kMagenta);
            gr50->SetLineStyle(3);
            gr50->SetLineWidth(2);
            gr50->Draw("l same");
        }
    }
 
 //File dat5 should contain a modelling curve of the broad-band SED data with the following format: freq, flux,
    std::ifstream In51;
    //  TGraph* gr5 = new TGraph(dat5.Data());
    TGraph* gr51 = new TGraph();
    i=0;
    if (dat51 == ""){
        cout<<"FILE 51 NOT DEFINED....SKIPPING IT"<<endl;
    }
    else{
        In51.open(dat51);
        if(!(In51)){
            cout<<"FILE "<<dat51.Data()<<" WAS NOT FOUND"<<endl;
            return;
        }
        else{
            cout<<"READING FILE "<<dat51.Data()<<" ..."<<endl;
          
            while(!In51.eof()) {
                line.ReadLine(In51);
                if((line.BeginsWith("/")) || (line.BeginsWith("!"))){
                    continue;
                }
                if(sscanf((const char *)line,"%f %f", &nu, &flux)==2){
                    gr51->SetPoint(i,nu,flux);
                    i++;
                }
                else{
                    cout << "FILE "<<dat51.Data()<<" COULD NOT BE READ!" << endl;
                    return;
                }
            }
            gr51->SetLineColor(kMagenta);
            gr51->SetLineStyle(5);
            gr51->SetLineWidth(2);
            gr51->Draw("l same");
        }
    }
  //File dat5 should contain a modelling curve of the broad-band SED data with the following format: freq, flux,
    std::ifstream In52;
    //  TGraph* gr5 = new TGraph(dat5.Data());
    TGraph* gr52 = new TGraph();
    i=0;
    if (dat52 == ""){
        cout<<"FILE 52 NOT DEFINED....SKIPPING IT"<<endl;
    }
    else{
        In52.open(dat52);
        if(!(In52)){
            cout<<"FILE "<<dat52.Data()<<" WAS NOT FOUND"<<endl;
            return;
        }
        else{
            cout<<"READING FILE "<<dat52.Data()<<" ..."<<endl;
          
            while(!In52.eof()) {
                line.ReadLine(In52);
                if((line.BeginsWith("/")) || (line.BeginsWith("!"))){
                    continue;
                }
                if(sscanf((const char *)line,"%f %f", &nu, &flux)==2){
                    gr52->SetPoint(i,nu,flux);
                    i++;
                }
                else{
                    cout << "FILE "<<dat52.Data()<<" COULD NOT BE READ!" << endl;
                    return;
                }
            }
            gr52->SetLineColor(kMagenta);
            gr52->SetLineStyle(4);
            gr52->SetLineWidth(2);
            gr52->Draw("l same");
        }

    }

    TLegend *leg=new TLegend(0.2,0.13,0.5,0.25);
    leg->SetFillColor(kWhite);
    // leg->Set
    //    leg->AddEntry(gr1,"Modelled data", "ep");
    leg->AddEntry(gr4,"SSC", "l");
    leg->AddEntry(gr3,"Spine-layer model", "l");
    leg->AddEntry(gr50,"Lepto-hadronic model", "l");
  

    leg->Draw();

}



